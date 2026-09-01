"""Security regression tests for the GitHub webhook endpoint."""

import hashlib
import hmac
import os
import unittest
from unittest.mock import patch

import httpx

from app.api.webhooks import verify_github_signature
from app.main import app


PAYLOAD = b'{"zen":"Keep it logically awesome."}'
SECRET = "test-webhook-secret"


def sha256_signature(payload: bytes = PAYLOAD, secret: str = SECRET) -> str:
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


class GitHubSignatureTests(unittest.TestCase):
    def test_missing_secret_fails_closed(self):
        with patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": ""}):
            self.assertFalse(verify_github_signature(PAYLOAD, sha256_signature()))

    def test_valid_sha256_signature_is_accepted(self):
        self.assertTrue(
            verify_github_signature(PAYLOAD, sha256_signature(), secret=SECRET)
        )

    def test_invalid_signature_is_rejected(self):
        self.assertFalse(
            verify_github_signature(PAYLOAD, "sha256=not-the-digest", secret=SECRET)
        )

    def test_legacy_sha1_signature_is_rejected(self):
        digest = hmac.new(SECRET.encode(), PAYLOAD, hashlib.sha1).hexdigest()
        self.assertFalse(
            verify_github_signature(PAYLOAD, f"sha1={digest}", secret=SECRET)
        )

    def test_malformed_signature_is_rejected(self):
        self.assertFalse(verify_github_signature(PAYLOAD, "malformed", secret=SECRET))


class GitHubWebhookEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def post_webhook(self, signature: str | None):
        headers = {
            "content-type": "application/json",
            "x-github-event": "ping",
            "x-github-delivery": "test-delivery",
        }
        if signature is not None:
            headers["x-hub-signature-256"] = signature

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.post(
                "/webhooks/github",
                content=PAYLOAD,
                headers=headers,
            )

    async def test_missing_secret_returns_service_unavailable(self):
        with patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": ""}):
            response = await self.post_webhook(sha256_signature())

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["detail"],
            "GitHub webhook verification is not configured",
        )

    async def test_invalid_signature_remains_unauthorized(self):
        with patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": SECRET}):
            response = await self.post_webhook("sha256=invalid")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid signature")

    async def test_missing_signature_is_unauthorized(self):
        with patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": SECRET}):
            response = await self.post_webhook(None)

        self.assertEqual(response.status_code, 401)

    async def test_malformed_signature_is_unauthorized(self):
        with patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": SECRET}):
            response = await self.post_webhook("malformed")

        self.assertEqual(response.status_code, 401)

    async def test_valid_signature_is_accepted(self):
        with patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": SECRET}):
            response = await self.post_webhook(sha256_signature())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "accepted")


if __name__ == "__main__":
    unittest.main()
