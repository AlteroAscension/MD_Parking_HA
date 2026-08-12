import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0, str(Path(__file__).parents[1] / "rootfs/usr/lib/python3.13/site-packages")
)

from md_parking_bridge.provider import Client, ProviderError, Session


class Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


class ProviderTest(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_object_required_is_normal_first_stage(self, urlopen):
        urlopen.return_value = Response(
            {"error": {"code": -32099, "message": "object required"}}
        )
        client = Client("https://auth.mdparking.ru/", {}, "mdparking", "")
        self.assertEqual(client.request_code("70000000000"), {"objectRequired": True})
        request = urlopen.call_args.args[0]
        self.assertEqual(
            list(json.loads(request.data)), ["params", "method", "jsonrpc", "id"]
        )
        self.assertNotIn(b" ", request.data)
        self.assertEqual(request.headers["App-platform"], "android")
        self.assertEqual(request.headers["Accept"], "application/json, text/plain, */*")

    @patch("urllib.request.urlopen")
    def test_object_required_after_object_id_remains_error(self, urlopen):
        urlopen.return_value = Response(
            {"error": {"code": -32099, "message": "object required"}}
        )
        client = Client("https://auth.mdparking.ru/", {}, "mdparking", "")
        with self.assertRaises(ProviderError) as caught:
            client.request_code("70000000000", "0000")
        self.assertEqual(caught.exception.safe_code, "object_required")

    @patch("urllib.request.urlopen")
    def test_stream_prefers_nested_high_resolution_source(self, urlopen):
        urlopen.return_value = Response(
            {
                "result": {
                    "stream": {
                        "hiRes": "rtsp://vs4.mdparking.ru/high",
                        "lowRes": "rtsp://vs4.mdparking.ru/low",
                    }
                }
            }
        )
        client = Client("https://auth.mdparking.ru/", {}, "mdparking", "")
        client.session = Session("access", "refresh", "https://app.mdparking.ru/")
        self.assertEqual(client.stream("channel"), "rtsp://vs4.mdparking.ru/high")

    @patch("urllib.request.urlopen")
    def test_stream_uses_nested_low_resolution_fallback(self, urlopen):
        urlopen.return_value = Response(
            {
                "result": {
                    "stream": {"hiRes": "", "lowRes": "rtsp://vs4.mdparking.ru/low"}
                }
            }
        )
        client = Client("https://auth.mdparking.ru/", {}, "mdparking", "")
        client.session = Session("access", "refresh", "https://app.mdparking.ru/")
        self.assertEqual(client.stream("channel"), "rtsp://vs4.mdparking.ru/low")

    @patch("urllib.request.urlopen")
    def test_authorize_persist_reload_and_inventory(self, urlopen):
        urlopen.side_effect = [
            Response(
                {
                    "result": {
                        "accessToken": "access",
                        "refreshToken": "refresh",
                        "appServer": "https://app.mdparking.ru/",
                    }
                }
            ),
            Response({"result": {"objects": [{"id": "one"}]}}),
        ]
        client = Client(
            "https://auth.mdparking.ru/",
            {"os": "android", "ver": "2.0.6"},
            "mdparking",
            "",
        )
        client.authorize("phone", "object", "code")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            client.save_session(path)
            restored = Client("https://auth.mdparking.ru/", {}, "mdparking", "")
            self.assertTrue(restored.load_session(path))
        self.assertEqual(client.inventory(), [{"id": "one"}])
        inventory_body = json.loads(urlopen.call_args_list[1].args[0].data)
        self.assertEqual(inventory_body["params"], {"id": "all"})

    @patch("urllib.request.urlopen")
    def test_refresh_sends_current_access_token_as_bearer(self, urlopen):
        urlopen.return_value = Response(
            {
                "result": {
                    "accessToken": "new-access",
                    "refreshToken": "new-refresh",
                    "appServer": "https://app.mdparking.ru/",
                }
            }
        )
        client = Client(
            "https://auth.mdparking.ru/",
            {"os": "android", "ver": "2.0.6"},
            "mdparking",
            "",
        )
        client.session = Session(
            "current-access", "current-refresh", "https://app.mdparking.ru/"
        )
        session = client.refresh_session()
        request = urlopen.call_args.args[0]
        self.assertEqual(request.headers["Authorization"], "Bearer current-access")
        self.assertEqual(session.access_token, "new-access")

    def test_rejects_untrusted_provider_host(self):
        with self.assertRaisesRegex(ProviderError, "not allowed"):
            Client("https://untrusted.example/", {}, "mdparking", "")

    @patch("urllib.request.urlopen")
    def test_rejects_non_object_json_rpc_payload(self, urlopen):
        urlopen.return_value = Response(["unexpected"])
        client = Client("https://auth.mdparking.ru/", {}, "mdparking", "")
        with self.assertRaises(ProviderError) as caught:
            client.request_code("70000000000")
        self.assertEqual(caught.exception.safe_code, "invalid_json_shape")

    def test_load_session_rejects_non_object_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            path.write_text("[]", encoding="utf-8")
            client = Client("https://auth.mdparking.ru/", {}, "mdparking", "")
            self.assertFalse(client.load_session(path))
