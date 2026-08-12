import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parents[1] / "rootfs/usr/lib/python3.13/site-packages")
)

from md_parking_bridge.redaction import redact_headers, redact_url


class RedactionTest(unittest.TestCase):
    def test_redact_url_removes_capability_path_and_query(self):
        self.assertEqual(
            redact_url("rtsp://video.example.test/private/path?signature=secret"),
            "rtsp://video.example.test/<redacted>",
        )

    def test_redact_headers_removes_authorization_values(self):
        self.assertEqual(
            redact_headers(
                {"Authorization": "Bearer secret", "Accept": "application/json"}
            ),
            {"Authorization": "<redacted>", "Accept": "application/json"},
        )

    def test_redact_url_removes_embedded_credentials(self):
        self.assertEqual(
            redact_url("rtsp://user:password@video.example.test:8554/private"),
            "rtsp://video.example.test:8554/<redacted>",
        )
