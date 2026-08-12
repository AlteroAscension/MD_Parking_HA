# Recording with Frigate

MD Parking Bridge exposes stable local RTSP restreams that can be recorded by
Frigate without storing the provider's short-lived signed source URLs. Copy the
per-camera addresses from **MD Parking > Подключение к видеорегистратору** in
Home Assistant.

## Recommended deployment

For Home Assistant OS, install the stable Frigate app from its official app
repository:

```text
https://github.com/blakeblackshear/frigate-hass-addons
```

Keep the MD Parking Bridge and Frigate on the same trusted LAN. Do not expose
either RTSP port to the internet. Use network storage for retention longer than
a short local test archive.

Start with continuous recording for six hours and object detection disabled.
This validates stream stability and bounds disk use before enabling additional
processing. Both MD Parking streams currently contain H.264 video without
audio, so recording does not need audio transcoding.

## Minimal Frigate configuration

Replace each placeholder with the corresponding stable address shown by the MD
Parking dashboard. Supply a local MQTT account if the Frigate Home Assistant
integration will be used; keep its password only in the live Frigate
configuration, never in Git.

```yaml
mqtt:
  enabled: true
  host: core-mosquitto
  port: 1883
  user: <LOCAL_MQTT_USER>
  password: <LOCAL_MQTT_PASSWORD>

go2rtc:
  streams:
    md_parking_1:
      - <STABLE_CAMERA_1_RTSP_URL>
    md_parking_2:
      - <STABLE_CAMERA_2_RTSP_URL>

cameras:
  md_parking_1:
    ffmpeg:
      inputs:
        - path: rtsp://127.0.0.1:8554/md_parking_1
          input_args: preset-rtsp-restream
          roles: [record]
    detect:
      enabled: false
    audio:
      enabled: false
    record:
      enabled: true
      continuous:
        days: 0.25

  md_parking_2:
    ffmpeg:
      inputs:
        - path: rtsp://127.0.0.1:8554/md_parking_2
          input_args: preset-rtsp-restream
          roles: [record]
    detect:
      enabled: false
    audio:
      enabled: false
    record:
      enabled: true
      continuous:
        days: 0.25

record:
  enabled: true

birdseye:
  enabled: false

snapshots:
  enabled: false
```

Frigate may still decode a camera stream for its live view and internal image
pipeline even when object detection is disabled. Check CPU, memory, and disk
usage after enabling both cameras. Increase retention only after measuring the
actual recorded bitrate.

## Smaller recording stream

If direct recording uses too much disk space, keep the original stream for live
view and create a separate software-transcoded stream for the `record` role.
The following profile limits the archive to 1280x720, 10 FPS, and approximately
800 kbit/s while leaving the named live stream unchanged:

```yaml
go2rtc:
  streams:
    camera_1:
      - <STABLE_CAMERA_1_RTSP_URL>
    camera_1_record:
      - "ffmpeg:camera_1#video=h264#width=1280#height=720#bitrate=800k#raw=-r 10"

cameras:
  camera_1:
    ffmpeg:
      inputs:
        - path: rtsp://127.0.0.1:8554/camera_1_record
          input_args: preset-rtsp-restream
          roles: [record]
    live:
      streams:
        Original: camera_1
```

Apply the same pattern to each camera. This reduces storage use but consumes
more CPU because FFmpeg must decode and encode every frame. Confirm the output
resolution and frame rate, measure several complete recording segments, and
restore direct recording if the host cannot sustain the additional load.

## Home Assistant integration

The Frigate app performs recording. The separate Frigate integration exposes
its cameras, recording controls, events, and media browser to Home Assistant.
Install the integration through HACS, connect it to the local Frigate instance,
and ensure both Frigate and Home Assistant use the same MQTT broker.

This recorder path is independent of barrier control. Frigate receives video
only and cannot call the barrier action API.
