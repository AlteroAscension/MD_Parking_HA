import sys
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0, str(Path(__file__).parents[1] / "rootfs/usr/lib/python3.13/site-packages")
)

from md_parking_bridge import main
from md_parking_bridge.main import State


class PhoneNormalizationTest(unittest.TestCase):
    def test_accepts_common_russian_formats(self):
        self.assertEqual(State._phone("+7 (999) 123-45-67"), "79991234567")
        self.assertEqual(State._phone("8 999 123 45 67"), "79991234567")
        self.assertEqual(State._phone("9991234567"), "79991234567")

    def test_rejects_invalid_phone(self):
        with self.assertRaises(ValueError):
            State._phone("123")


class RuntimeOptionsTest(unittest.TestCase):
    def test_reload_applies_mutable_switches(self):
        class Control:
            enabled = False
            cooldown_seconds = 15

            def configure(self, enabled, cooldown_seconds):
                self.enabled = enabled
                self.cooldown_seconds = cooldown_seconds

        class Bridge:
            refresh_seconds = 45

        with tempfile.TemporaryDirectory() as directory:
            options = Path(directory) / "options.json"
            options.write_text(
                json.dumps(
                    {
                        "pairing_enabled": True,
                        "control_enabled": True,
                        "control_cooldown_seconds": 30,
                        "refresh_before_expiry_seconds": 20,
                    }
                ),
                encoding="utf-8",
            )
            state = State.__new__(State)
            state.lock = threading.RLock()
            state.options = {}
            state._options_mtime_ns = 0
            state.pairing_enabled = False
            state.control = Control()
            state.bridge = Bridge()
            with patch.object(main, "OPTIONS", options):
                state.reload_options()
            self.assertTrue(state.pairing_enabled)
            self.assertTrue(state.control.enabled)
            self.assertEqual(state.control.cooldown_seconds, 30)
            self.assertEqual(state.bridge.refresh_seconds, 40)
