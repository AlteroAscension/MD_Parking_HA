import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "rootfs/usr/lib/python3.13/site-packages"))

from md_parking_bridge.bridge import Bridge
from md_parking_bridge.restream import Go2Rtc


class FakeClient:
    def inventory(self): return [{"id": "object-secret"}]
    def checkpoints(self, object_id):
        assert object_id == "object-secret"
        return [{"id": "checkpoint-secret", "name": "Entrance", "channel": "camera-channel"}]
    def stream(self, channel):
        assert channel == "camera-channel"
        return "rtsp://provider.invalid/private?signed=secret"


class FakeRestream:
    stable_name = staticmethod(Go2Rtc.stable_name)
    def __init__(self): self.updated = []
    def replace_source(self, name, source): self.updated.append((name, source))


class BridgeTest(unittest.TestCase):
    def test_discovery_hashes_provider_identifier_and_refreshes_source(self):
        restream = FakeRestream()
        bridge = Bridge(FakeClient(), restream, refresh_seconds=45)
        cameras = bridge.discover()
        self.assertEqual(len(cameras), 1)
        self.assertNotIn("checkpoint-secret", cameras[0].stream_name)
        bridge.refresh_due()
        self.assertEqual(restream.updated[0][0], cameras[0].stream_name)
        self.assertTrue(restream.updated[0][1].startswith("rtsp://"))


class RestreamTest(unittest.TestCase):
    def test_stable_name_is_repeatable_and_redacted(self):
        first = Go2Rtc.stable_name("raw-provider-id")
        self.assertEqual(first, Go2Rtc.stable_name("raw-provider-id"))
        self.assertNotIn("raw-provider-id", first)
