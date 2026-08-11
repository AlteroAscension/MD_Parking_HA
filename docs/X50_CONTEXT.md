# X50 context and cross-references

## Independence rule

MD Parking HA is a separate project. It must not change X50 Gateway, Navigation,
Relay, Media Bridge, simulator code or their release channels. The common AVD is
the only intentional shared component for now.

## Local source project

The current X50 workspace is located at:

```text
C:\Users\alter\YandexDisk\Projects\X50_telemetry
```

Its public umbrella repository is
[AlteroAscension/X50_telemetry](https://github.com/AlteroAscension/X50_telemetry).

Useful local documentation when emulator behaviour or existing HA conventions
matter:

- `C:\Users\alter\YandexDisk\Projects\X50_telemetry\README.md`
- `C:\Users\alter\YandexDisk\Projects\X50_telemetry\Yandex_navi\FAKE_GPS_TEST_MODE.md`
- `C:\Users\alter\YandexDisk\Projects\X50_telemetry\x50-navigation\README.md`
- `C:\Users\alter\YandexDisk\Projects\X50_telemetry\belgee-x50-ha-integration\README.md`

## Things that may be reused conceptually, not copied blindly

| X50 concept | MD Parking use |
| --- | --- |
| HA add-on plus custom integration | Preferred split between bridge and HA entities |
| Local-only secret handling | Template for provider credentials and diagnostics |
| Shared AVD and ADB scripts | Test infrastructure only |
| Release/update channel separation | Future delivery pattern if this becomes distributable |

MD Parking must use its own package names, add-on slug, Git repository, release
channel and documentation. It must never reuse an X50 control token, VPN route
or Home Assistant webhook as a shortcut.
