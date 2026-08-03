import os
import unittest
from grok_client import build_request_payload, get_grok_api_key


class TestGrokClient(unittest.TestCase):

    def test_build_request_payload_uses_defaults(self):
        old_env = os.environ.pop("GROK_API_KEY", None)
        try:
            payload = build_request_payload("Hello")
            self.assertEqual(payload["model"], "grok-2-latest")
            self.assertEqual(payload["messages"][0]["role"], "user")
            self.assertEqual(payload["messages"][0]["content"], "Hello")
        finally:
            if old_env is not None:
                os.environ["GROK_API_KEY"] = old_env

    def test_get_grok_api_key_raises_when_missing(self):
        old_grok = os.environ.pop("GROK_API_KEY", None)
        try:
            self.assertIsNone(get_grok_api_key())
        finally:
            if old_grok is not None:
                os.environ["GROK_API_KEY"] = old_grok


if __name__ == "__main__":
    unittest.main()
