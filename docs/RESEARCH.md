# Initial provider research

## Scope and method

The work is limited to the user's authenticated MD Parking account and passive
observation of the official Android client. No barrier-open action was invoked.
Temporary captures and the installed APK are local-only artefacts under
`.local/` and are not repository content.

## Observed Android application

| Item | Finding |
| --- | --- |
| Package | `ru.mdparking.application` |
| Version | 2.0.6 / versionCode 68 |
| UI/runtime | React Native with native VLC player |
| API host | `app.mdparking.ru` |
| Auth host | `auth.mdparking.ru/v2` |
| API transport | HTTPS, validated TLS 1.3 certificate |
| Video transport | RTSP over TCP to `vs4.mdparking.ru` on port `49054` |
| Decoded stream | 1280×720 observed in VLC logs |

## Stream model

When a camera detail is opened, the official client passes a URL of this form to
VLC (values intentionally redacted):

```text
rtsp://vs4.mdparking.ru:49054/app/<camera-specific-path>?wmsAuthSign=<signed-capability>
```

`wmsAuthSign` is an encoded signed server-side capability. Its decoded metadata
observed a `validminutes=1` policy. It must be treated as a temporary bearer
credential, not as a static camera address.

The API request that delivers the source is HTTPS-protected. RTSP itself is not
TLS-wrapped (`rtsp://`, not `rtsps://`), so the short expiry/signature is the
main protection of the media connection.

## What is known and unknown

Known:

- The account has two barrier/camera objects.
- The application can obtain and decode a signed stream.
- The provider refreshes/reissues a source URL when the camera detail is opened.

Still to determine safely:

- precise read-only API request and response schema;
- whether RTSP stays alive after the one-minute capability expiry;
- whether a capability is tied to client IP/session;
- source-refresh rate limit and failure behaviour;
- whether the same API authorisation is also accepted for a read-only service
outside the Android app.

## Security conclusion

The provider is not exposing a permanent anonymous camera. It uses an
authenticated HTTPS control plane and a short-lived signed RTSP capability.
Do not test unsigned URLs, guess camera identifiers, scan provider hosts or
attempt to bypass the signing system. The integration should reproduce only the
normal authorised source-acquisition flow, with the user's consent.
