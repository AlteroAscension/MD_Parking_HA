import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parents[1] / "rootfs/usr/lib/python3.13/site-packages")
)

from md_parking_bridge.main import State


class PhoneNormalizationTest(unittest.TestCase):
    def test_accepts_common_russian_formats(self):
        self.assertEqual(State._phone("+7 (999) 123-45-67"), "79991234567")
        self.assertEqual(State._phone("8 999 123 45 67"), "79991234567")
        self.assertEqual(State._phone("9991234567"), "79991234567")

    def test_rejects_invalid_phone(self):
        with self.assertRaises(ValueError):
            State._phone("123")
