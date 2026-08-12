FROM ghcr.io/home-assistant/amd64-base-python:3.13-alpine3.21

ARG BUILD_VERSION=0.4.1
ARG GO2RTC_VERSION=1.9.9
ARG GO2RTC_SHA256=aca941066c816cd69f4d689bf556f924057f5087449c2fdd7d5854d9aaec8ea9

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="amd64"

RUN apk add --no-cache curl \
    && curl --fail --silent --show-error --location \
      "https://github.com/AlexxIT/go2rtc/releases/download/v${GO2RTC_VERSION}/go2rtc_linux_amd64" \
      --output /usr/local/bin/go2rtc \
    && echo "${GO2RTC_SHA256}  /usr/local/bin/go2rtc" | sha256sum -c - \
    && chmod 0755 /usr/local/bin/go2rtc

COPY rootfs /
RUN chmod 0755 /etc/services.d/md-parking-bridge/run
