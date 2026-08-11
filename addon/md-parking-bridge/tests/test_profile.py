import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "rootfs/usr/lib/python3.13/site-packages"))

from md_parking_bridge.profile import ProfileError, load_profile


def profile():
    return {
        "version": 1,
        "allowed_hosts": ["auth.example.test", "api.example.test"],
        "auth": {"method": "POST", "url": "https://auth.example.test/session", "headers": {}},
        "cameras": {"method": "GET", "url": "https://api.example.test/cameras", "headers": {}},
        "token_path": "access_token",
        "items_path": "items",
        "alias_path": "name",
        "source_path": "source",
    }


class ProfileTest(unittest.TestCase):
    def write_profile(self, value):
        path = Path(self.temporaryDirectory.name) / "profile.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def setUp(self):
        self.temporaryDirectory = __import__("tempfile").TemporaryDirectory()

    def tearDown(self):
        self.temporaryDirectory.cleanup()

    def test_loads_confirmed_read_only_profile(self):
        self.assertEqual(load_profile(self.write_profile(profile())).cameras.method, "GET")

    def test_rejects_control_like_path(self):
        value = profile()
        value["cameras"]["url"] = "https://api.example.test/barrier/open"
        with self.assertRaisesRegex(ProfileError, "forbidden"):
            load_profile(self.write_profile(value))

    def test_rejects_unlisted_host(self):
        value = profile()
        value["auth"]["url"] = "https://untrusted.example.test/session"
        with self.assertRaisesRegex(ProfileError, "allow-list"):
            load_profile(self.write_profile(value))
