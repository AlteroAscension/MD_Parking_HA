import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parents[1] / "rootfs/usr/lib/python3.13/site-packages")
)

from md_parking_bridge.bridge import Bridge
from md_parking_bridge.restream import Go2Rtc


class FakeClient:
    def inventory(self):
        return [{"id": "object-secret"}]

    def checkpoints(self, object_id):
        assert object_id == "object-secret"
        return [
            {"id": "checkpoint-secret", "name": "Entrance", "channel": "camera-channel"}
        ]

    def stream(self, channel):
        assert channel == "camera-channel"
        return "rtsp://vs4.mdparking.ru/private?signed=secret"

    def access(self, acs_id):
        return {"status": "OK"}


class FakeRestream:
    stable_name = staticmethod(Go2Rtc.stable_name)

    def __init__(self):
        self.updated = []

    def replace_source(self, name, source):
        self.updated.append((name, source))


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

    def test_barrier_identifier_is_hashed_and_control_is_explicit(self):
        client = FakeClient()
        client.checkpoints = lambda object_id: [
            {
                "id": "checkpoint-secret",
                "name": "Gate",
                "channel": "camera-channel",
                "acsId": "access-secret",
            }
        ]
        bridge = Bridge(client, FakeRestream(), refresh_seconds=45)
        bridge.discover()
        barrier = next(iter(bridge.barriers.values()))
        self.assertNotIn("checkpoint-secret", barrier.barrier_id)
        self.assertEqual(bridge.open_barrier(barrier.barrier_id), {"status": "OK"})


class RestreamTest(unittest.TestCase):
    def test_stable_name_is_repeatable_and_redacted(self):
        first = Go2Rtc.stable_name("raw-provider-id")
        self.assertEqual(first, Go2Rtc.stable_name("raw-provider-id"))
        self.assertNotIn("raw-provider-id", first)


class PartiallyFailingClient(FakeClient):
    def checkpoints(self, object_id):
        return [
            {"id": "bad", "name": "Bad", "channel": "bad-channel"},
            {"id": "good", "name": "Good", "channel": "good-channel"},
        ]

    def stream(self, channel):
        if channel == "bad-channel":
            raise RuntimeError("temporary failure")
        return "rtsp://vs4.mdparking.ru/good"


class RefreshIsolationTest(unittest.TestCase):
    def test_failure_of_one_camera_does_not_block_other_camera(self):
        restream = FakeRestream()
        bridge = Bridge(PartiallyFailingClient(), restream, refresh_seconds=45)
        bridge.discover()
        with self.assertRaises(RuntimeError):
            bridge.refresh_due()
        self.assertEqual(len(restream.updated), 1)
        self.assertEqual(restream.updated[0][0], Go2Rtc.stable_name("good"))
