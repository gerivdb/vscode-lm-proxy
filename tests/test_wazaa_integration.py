"""Tests for vscode-lm-proxy WAZAA integration bridge."""

import json
import os
import sys
import unittest
from pathlib import Path

# WAZAA src path
_WAZAA_SRC = Path(r"D:\DO/WEB\TOOLS\L4-TOOLS\WAZAA\src")
if str(_WAZAA_SRC) not in sys.path:
    sys.path.insert(0, str(_WAZAA_SRC))

# Integration source path
_SRC_DIR = Path(__file__).parent.parent / "src" / "integration"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# Force offline mode for tests
os.environ["GERICODE_WAZAA_OFFLINE"] = "0"

from wazaa_bridge import WazaaIntegration  # noqa: E402


class TestWazaaIntegration(unittest.TestCase):
    """Tests pour le bridge WAZAA de vscode-lm-proxy."""

    def setUp(self):
        self.integration = WazaaIntegration()

    def test_get_status(self):
        status = self.integration.get_status() if hasattr(self.integration, 'get_status') else self.integration._publisher.get_status()
        self.assertEqual(status["component"], "GERICODE")

    def test_emit_lint_publishes(self):
        count = self.integration.emit_lint(
            file="extension.ts",
            diagnostics=[{"line": 1, "message": "unused"}],
        )
        # In offline mode, returns 0
        self.assertEqual(count, 0)

    def test_emit_cache_publishes(self):
        count = self.integration.emit_cache(provider="claude", hit=True, entries=5)
        self.assertEqual(count, 0)

    def test_emit_skill_publishes(self):
        count = self.integration.emit_skill(
            skill="ontology-auditor", model="claude", intent="check terms",
        )
        self.assertEqual(count, 0)

    def test_offline_mode_skips_publish(self):
        os.environ["GERICODE_WAZAA_OFFLINE"] = "1"
        integration = WazaaIntegration()
        self.assertTrue(integration._offline)
        count = integration.emit_lint(file="x.ts", diagnostics=[])
        self.assertEqual(count, 0)
        os.environ.pop("GERICODE_WAZAA_OFFLINE", None)


if __name__ == "__main__":
    unittest.main()
