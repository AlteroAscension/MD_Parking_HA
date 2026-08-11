import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "rootfs/usr/lib/python3.13/site-packages"))

from md_parking_bridge.provider import Client


class Response:
    def __init__(self, payload): self.payload = payload
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self): return json.dumps(self.payload).encode()


class ProviderTest(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_authorize_persist_reload_and_inventory(self, urlopen):
        urlopen.side_effect = [
            Response({"result": {"accessToken": "access", "refreshToken": "refresh", "appServer": "https://api.invalid/"}}),
            Response({"result": {"objects": [{"id": "one"}]}}),
        ]
        client = Client("https://auth.invalid/", {"os": "android", "ver": "2.0.6"}, "mdparking", "")
        client.authorize("phone", "object", "code")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            client.save_session(path)
            restored = Client("https://auth.invalid/", {}, "mdparking", "")
            self.assertTrue(restored.load_session(path))
        self.assertEqual(client.inventory(), [{"id": "one"}])
        inventory_body = json.loads(urlopen.call_args_list[1].args[0].data)
        self.assertEqual(inventory_body["params"], {"id": "all"})
