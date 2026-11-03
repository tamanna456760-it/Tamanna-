FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends tor ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && install -d -o debian-tor -g debian-tor -m 0700 /var/lib/tor/hidden_service

COPY deploy/tor/torrc /etc/tor/torrc
RUN chown root:root /etc/tor/torrc && chmod 0644 /etc/tor/torrc

USER debian-tor
CMD ["tor", "-f", "/etc/tor/torrc"]
