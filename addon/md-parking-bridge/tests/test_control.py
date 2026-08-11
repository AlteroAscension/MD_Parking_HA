import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "rootfs/usr/lib/python3.13/site-packages"))

from md_parking_bridge.control import (
    ConfirmationRequired,
    ControlDisabled,
    ControlManager,
    RateLimited,
)


class FakeBridge:
    def __init__(self): self.calls = []
    def open_barrier(self, barrier_id):
        self.calls.append(barrier_id)
        return {"status": "OK"}


class ControlTest(unittest.TestCase):
    def test_control_requires_enable_and_confirmation(self):
        bridge = FakeBridge()
        with self.assertRaises(ControlDisabled):
            ControlManager(False).open(bridge, "safe-id", True)
        with self.assertRaises(ConfirmationRequired):
            ControlManager(True).open(bridge, "safe-id", False)
        self.assertEqual(bridge.calls, [])

    def test_success_is_audited_and_rate_limited(self):
        bridge = FakeBridge(); manager = ControlManager(True, 15)
        result = manager.open(bridge, "safe-id", True)
        self.assertEqual(result["result"], "accepted")
        self.assertEqual(manager.audit()[0]["barrier_id"], "safe-id")
        with self.assertRaises(RateLimited): manager.open(bridge, "safe-id", True)
        self.assertEqual(bridge.calls, ["safe-id"])
