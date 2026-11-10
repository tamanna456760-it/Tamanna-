"""Read-only, bounded retrieval of public HTTPS pages and source text."""
from __future__ import annotations

import asyncio
import ipaddress
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

import aiohttp


class WebFetchError(RuntimeError):
    """A URL could not be safely or successfully retrieved."""


class _PinnedPublicResolver:
    """Resolve once per connection and hand aiohttp only validated public IPs.

    aiohttp connects to the returned numeric address but retains the original
    URL hostname for the HTTP Host header and TLS SNI/certificate validation.
    """

    def __init__(self, lookup=None):
        self._lookup = lookup

    async def resolve(self, host, port=0, family=socket.AF_UNSPEC):
        loop = asyncio.get_running_loop()
        lookup = self._lookup or loop.getaddrinfo
        try:
            records = await lookup(
                host, port, family=family, type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            )
        except (OSError, ValueError) as exc:
            raise OSError("Hostname could not be resolved") from exc

        validated = []
        seen = set()
        for record in records:
            address = ipaddress.ip_address(record[4][0].split("%", 1)[0])
            if not address.is_global:
                raise OSError("Private, local, reserved, or non-public IP addresses are blocked")
            key = (str(address), record[0])
            if key in seen:
                continue
            seen.add(key)
            validated.append({
                "hostname": host,
                "host": str(address),
                "port": port,
                "family": record[0],
                "proto": record[2],
                "flags": record[3],
            })
        if not validated:
            raise OSError("Hostname returned no usable public addresses")
        return validated

    async def close(self):
        return None


class _PageText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.title_parts = []
        self.skip = 0
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "template"}:
            self.skip += 1
        if tag == "title":
            self.in_title = True
        if tag in {"p", "div", "br", "li", "h1", "h2", "h3", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "template"} and self.skip:
            self.skip -= 1
        if tag == "title":
            self.in_title = False
        if tag in {"p", "div", "br", "li", "h1", "h2", "h3", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_title:
            self.title_parts.append(data)
        self.parts.append(data)


class SafeWebFetcher:
    """Fetch explicitly supplied public HTTPS URLs; never execute fetched content."""

    def __init__(self, *, timeout=12.0, max_bytes=1_000_000, max_redirects=3):
        if not 0 < timeout <= 30:
            raise ValueError("timeout must be between 0 and 30 seconds")
        if not 1 <= max_bytes <= 5_000_000:
            raise ValueError("max_bytes must be between 1 and 5,000,000")
        if not 0 <= max_redirects <= 5:
            raise ValueError("max_redirects must be between 0 and 5")
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.max_redirects = max_redirects

    @staticmethod
    def _validate_url(url):
        if not isinstance(url, str) or len(url) > 2048:
            raise ValueError("URL must be a string of at most 2048 characters")
        parsed = urlsplit(url.strip())
        if parsed.scheme.lower() != "https" or not parsed.hostname:
            raise ValueError("Only absolute HTTPS URLs are allowed")
        if parsed.username or parsed.password:
            raise ValueError("Embedded URL credentials are not allowed")
        try:
            if parsed.port not in (None, 443):
                raise ValueError("Only standard HTTPS port 443 is allowed")
        except ValueError as exc:
            raise ValueError("Invalid URL port") from exc
        host = parsed.hostname.rstrip(".").encode("idna").decode("ascii").lower()
        if host == "localhost" or host.endswith(".localhost"):
            raise ValueError("Local hostnames are not allowed")
        try:
            addresses = [ipaddress.ip_address(host)]
        except ValueError:
            try:
                records = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
                addresses = [ipaddress.ip_address(item[4][0].split("%", 1)[0]) for item in records]
            except (OSError, ValueError) as exc:
                raise WebFetchError("Hostname could not be resolved") from exc
        if not addresses or any(not address.is_global for address in addresses):
            raise ValueError("Private, local, reserved, or non-public IP addresses are blocked")
        return url.strip()

    async def fetch(self, url, *, raw_source=False):
        """Fetch one text page with pinned DNS, redirect, type, timeout and size limits."""
        current = self._validate_url(url)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(
            resolver=_PinnedPublicResolver(),
            use_dns_cache=False,
            ssl=True,
        )
        headers = {
            "User-Agent": "TamannaAI-Reader/1.0",
            "Accept": "text/html,text/plain,application/json,application/xml,text/xml,text/css,application/javascript;q=0.9",
        }
        try:
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers,
                trust_env=False,
                auto_decompress=True,
            ) as client:
                for redirect_count in range(self.max_redirects + 1):
                    async with client.get(current, allow_redirects=False) as response:
                        if response.status in {301, 302, 303, 307, 308}:
                            location = response.headers.get("location")
                            if not location or redirect_count >= self.max_redirects:
                                raise WebFetchError("Redirect limit reached or Location missing")
                            current = self._validate_url(urljoin(current, location))
                            continue
                        response.raise_for_status()
                        content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
                        allowed = {
                            "text/html", "text/plain", "application/json", "application/xml",
                            "text/xml", "text/css", "application/javascript", "text/javascript",
                        }
                        if content_type not in allowed and not content_type.endswith(("+json", "+xml")):
                            raise WebFetchError("Only readable text pages and source files are accepted")
                        if response.content_length is not None and response.content_length > self.max_bytes:
                            raise WebFetchError("Response exceeds configured size limit")
                        body = bytearray()
                        async for chunk in response.content.iter_chunked(65536):
                            body.extend(chunk)
                            if len(body) > self.max_bytes:
                                raise WebFetchError("Response exceeds configured size limit")
                        encoding = response.charset or "utf-8"
                        try:
                            source = bytes(body).decode(encoding, errors="replace")
                        except LookupError:
                            source = bytes(body).decode("utf-8", errors="replace")
                        title, text = "", source
                        if content_type == "text/html" and not raw_source:
                            parser = _PageText()
                            parser.feed(source)
                            title = " ".join(" ".join(parser.title_parts).split())[:300]
                            text = " ".join("".join(parser.parts).split())
                        return {
                            "url": current, "title": title, "content_type": content_type,
                            "content": text[:self.max_bytes], "bytes": len(body),
                        }
        except WebFetchError:
            raise
        except (aiohttp.ClientError, OSError, ValueError) as exc:
            raise WebFetchError("Web retrieval failed: " + type(exc).__name__) from exc
        raise WebFetchError("Unable to retrieve URL")


__all__ = ["SafeWebFetcher", "WebFetchError"]
