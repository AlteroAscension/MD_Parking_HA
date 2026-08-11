ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG BUILD_ARCH
ARG GO2RTC_VERSION

RUN apk add --no-cache curl \
    && curl --fail --silent --show-error --location \
      "https://github.com/AlexxIT/go2rtc/releases/download/v${GO2RTC_VERSION}/go2rtc_linux_${BUILD_ARCH}" \
      --output /usr/local/bin/go2rtc \
    && chmod 0755 /usr/local/bin/go2rtc

COPY rootfs /
RUN chmod 0755 /etc/services.d/md-parking-bridge/run
