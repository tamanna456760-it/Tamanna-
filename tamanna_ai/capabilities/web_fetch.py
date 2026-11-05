"""Read-only, bounded retrieval of public HTTPS pages and source text."""
from __future__ import annotations

import ipaddress
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

import httpx


class WebFetchError(RuntimeError):
    """A URL could not be safely or successfully retrieved."""


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
        if parsed.port not in (None, 443):
            raise ValueError("Only standard HTTPS port 443 is allowed")
        host = parsed.hostname.rstrip(".").encode("idna").decode("ascii").lower()
        if host == "localhost" or host.endswith(".localhost"):
            raise ValueError("Local hostnames are not allowed")
        try:
            addresses = [ipaddress.ip_address(host)]
        except ValueError:
            try:
                records = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
                addresses = [ipaddress.ip_address(item[4][0]) for item in records]
            except (OSError, ValueError) as exc:
                raise WebFetchError("Hostname could not be resolved") from exc
        if not addresses or any(not address.is_global for address in addresses):
            raise ValueError("Private, local, reserved, or non-public IP addresses are blocked")
        return url.strip()

    async def fetch(self, url, *, raw_source=False):
        """Fetch one text page with redirect, content-type, timeout and size limits."""
        current = self._validate_url(url)
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=False,
                trust_env=False,
                headers={
                    "User-Agent": "TamannaAI-Reader/1.0",
                    "Accept": "text/html,text/plain,application/json,application/xml,text/xml,text/css,application/javascript;q=0.9",
                },
            ) as client:
                for redirect_count in range(self.max_redirects + 1):
                    async with client.stream("GET", current) as response:
                        if response.status_code in {301, 302, 303, 307, 308}:
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
                        declared = response.headers.get("content-length")
                        if declared and int(declared) > self.max_bytes:
                            raise WebFetchError("Response exceeds configured size limit")
                        body = bytearray()
                        async for chunk in response.aiter_bytes():
                            body.extend(chunk)
                            if len(body) > self.max_bytes:
                                raise WebFetchError("Response exceeds configured size limit")
                        encoding = response.encoding or "utf-8"
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
        except (httpx.HTTPError, ValueError) as exc:
            raise WebFetchError("Web retrieval failed: " + type(exc).__name__) from exc
        raise WebFetchError("Unable to retrieve URL")


__all__ = ["SafeWebFetcher", "WebFetchError"]
