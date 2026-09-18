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
            MAX_CONTENT_LENGTH=100 * 1024 * 1024,
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

    def test_successful_login_creates_authenticated_session(self):
        response = self.client.post(
            "/login",
            data={"pin": os.environ["LAN_DROP_PIN"]},
            base_url="https://localhost",
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")

        with self.client.session_transaction() as session:
            self.assertTrue(session["authenticated"])
            self.assertTrue(session["csrf_token"])

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

    def test_duplicate_filename_is_preserved_with_numbered_suffix(self):
        csrf_token = "test-csrf-token"
        self.authenticate(csrf_token)

        first_response = self.client.post(
            "/upload",
            data={
                "csrf_token": csrf_token,
                "file": (io.BytesIO(b"first"), "report.txt"),
            },
            content_type="multipart/form-data",
            base_url="https://localhost",
        )
        second_response = self.client.post(
            "/upload",
            data={
                "csrf_token": csrf_token,
                "file": (io.BytesIO(b"second"), "report.txt"),
            },
            content_type="multipart/form-data",
            base_url="https://localhost",
        )

        upload_directory = Path(self.upload_directory.name)
        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(second_response.status_code, 302)
        self.assertEqual((upload_directory / "report.txt").read_bytes(), b"first")
        self.assertEqual((upload_directory / "report_1.txt").read_bytes(), b"second")

    def test_oversized_upload_returns_413_without_writing_file(self):
        self.assertEqual(
            lan_drop.app.config["MAX_CONTENT_LENGTH"],
            100 * 1024 * 1024,
        )

        lan_drop.app.config["MAX_CONTENT_LENGTH"] = 1024
        csrf_token = "test-csrf-token"
        self.authenticate(csrf_token)

        response = self.client.post(
            "/upload",
            data={
                "csrf_token": csrf_token,
                "file": (io.BytesIO(b"x" * 2048), "oversized.bin"),
            },
            content_type="multipart/form-data",
            base_url="https://localhost",
        )

        self.assertEqual(response.status_code, 413)
        self.assertFalse(
            (Path(self.upload_directory.name) / "oversized.bin").exists()
        )

    def test_upload_download_delete_lifecycle(self):
        csrf_token = "test-csrf-token"
        self.authenticate(csrf_token)

        upload_response = self.client.post(
            "/upload",
            data={
                "csrf_token": csrf_token,
                "file": (io.BytesIO(b"lifecycle-content"), "lifecycle.txt"),
            },
            content_type="multipart/form-data",
            base_url="https://localhost",
        )
        download_response = self.client.get(
            "/download/lifecycle.txt",
            base_url="https://localhost",
        )
        downloaded_content = download_response.get_data()
        download_response.close()
        delete_response = self.client.post(
            "/delete/lifecycle.txt",
            data={"csrf_token": csrf_token},
            base_url="https://localhost",
        )

        self.assertEqual(upload_response.status_code, 302)
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(downloaded_content, b"lifecycle-content")
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(
            (Path(self.upload_directory.name) / "lifecycle.txt").exists()
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
