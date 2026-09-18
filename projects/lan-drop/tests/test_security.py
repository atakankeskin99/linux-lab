import io
import os
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault("LAN_DROP_SECRET", "test-secret-not-for-production")
os.environ.setdefault("LAN_DROP_PIN", "123456")

import app as lan_drop  # noqa: E402


class SecurityRegressionTests(unittest.TestCase):
    def setUp(self):
        self.upload_directory = tempfile.TemporaryDirectory()
        lan_drop.app.config.update(
            TESTING=True,
            UPLOAD_FOLDER=self.upload_directory.name,
        )
        lan_drop.failed_login_attempts.clear()
        self.client = lan_drop.app.test_client()

    def tearDown(self):
        self.upload_directory.cleanup()

    def authenticate(self, csrf_token="test-csrf-token"):
        with self.client.session_transaction() as session:
            session["authenticated"] = True
            session["csrf_token"] = csrf_token

    def test_unauthenticated_upload_is_redirected_to_login(self):
        response = self.client.post("/upload", base_url="https://localhost")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/login")

    def test_authenticated_upload_without_csrf_token_is_rejected(self):
        self.authenticate()

        response = self.client.post(
            "/upload",
            data={"file": (io.BytesIO(b"blocked"), "blocked.txt")},
            content_type="multipart/form-data",
            base_url="https://localhost",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse((Path(self.upload_directory.name) / "blocked.txt").exists())

    def test_valid_csrf_token_allows_upload_and_sanitizes_filename(self):
        csrf_token = "test-csrf-token"
        self.authenticate(csrf_token)

        response = self.client.post(
            "/upload",
            data={
                "csrf_token": csrf_token,
                "file": (io.BytesIO(b"safe"), "../../safe.txt"),
            },
            content_type="multipart/form-data",
            base_url="https://localhost",
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")
        self.assertEqual(
            (Path(self.upload_directory.name) / "safe.txt").read_bytes(),
            b"safe",
        )

    def test_sixth_failed_pin_attempt_remains_locked(self):
        for _ in range(lan_drop.MAX_LOGIN_ATTEMPTS):
            response = self.client.post(
                "/login",
                data={"pin": "000000"},
                base_url="https://localhost",
            )

        self.assertIn(b"Too many incorrect attempts", response.data)

        response = self.client.post(
            "/login",
            data={"pin": os.environ["LAN_DROP_PIN"]},
            base_url="https://localhost",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Too many incorrect attempts", response.data)


if __name__ == "__main__":
    unittest.main()
