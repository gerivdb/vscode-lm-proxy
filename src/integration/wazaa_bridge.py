#!/usr/bin/env python3
"""
vscode-lm-proxy WAZAA Integration — Publie les événements du proxy LM vers le bus WAZAA.

Intègre le vscode-lm-proxy au bus WAZAA en publiant :
- gericode_lint : diagnostics de schema/TypeScript
- gericode_cache : hit/miss du cache de providers
- gericode_skill : invocations de skills via LM proxy

Usage:
    # Direct
    python src/integration/wazaa_bridge.py --event lint --file extension.ts
    # Importé depuis extension.ts
    from integration.wazaa_bridge import WazaaIntegration
    wazaa = WazaaIntegration()
    wazaa.emit_lint(file="extension.ts", diagnostics=[...])
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

# WAZAA src path
_WAZAA_SRC = Path(r"D:\DO/WEB\TOOLS\L4-TOOLS\WAZAA\src")
if str(_WAZAA_SRC) not in sys.path:
    sys.path.insert(0, str(_WAZAA_SRC))

from publishers.gericode_publisher import GericodePublisher  # noqa: E402

logger_name = "vscode_lm_proxy.wazaa_bridge"
import logging  # noqa: E402
logger = logging.getLogger(logger_name)

_OFFLINE = os.environ.get("GERICODE_WAZAA_OFFLINE", "0") == "1"


class WazaaIntegration:
    """Bridge WAZAA pour vscode-lm-proxy.

    Publie les événements LM proxy sur le bus WAZAA via GericodePublisher.
    """

    def __init__(self, publisher: Optional[GericodePublisher] = None) -> None:
        self._publisher = publisher or GericodePublisher()
        self._offline = os.environ.get("GERICODE_WAZAA_OFFLINE", "0") == "1"

    def emit_lint(self, file: str, diagnostics: Optional[list[dict]] = None) -> int:
        """Publie un diagnostic de lint pour un fichier LM proxy."""
        if self._offline:
            return 0
        msg = {
            "event": "lint",
            "source": "vscode-lm-proxy",
            "file": file,
            "diagnostics": diagnostics or [],
        }
        return self._publisher.publish(msg, "gericode_lint")

    def emit_cache(self, provider: str, hit: bool, entries: int = 0) -> int:
        """Publie un événement de cache provider."""
        if self._offline:
            return 0
        msg = {
            "event": "cache",
            "source": "vscode-lm-proxy",
            "extension": f"lm-proxy-{provider}",
            "hit": hit,
            "entries": entries,
        }
        return self._publisher.publish(msg, "gericode_cache")

    def emit_skill(self, skill: str, model: str, intent: str) -> int:
        """Publie une invocation de skill via LM proxy."""
        if self._offline:
            return 0
        msg = {
            "event": "skill_invocation",
            "source": "vscode-lm-proxy",
            "skill": skill,
            "model": model,
            "intent": intent,
            "intent_hash": os.environ.get("KILO_INTENT_HASH", ""),
        }
        return self._publisher.publish(msg, "gericode_skill")


def main() -> int:
    parser = argparse.ArgumentParser(description="vscode-lm-proxy WAZAA bridge")
    parser.add_argument("--event", required=True, choices=["lint", "cache", "skill"])
    parser.add_argument("--file", help="File path for lint events")
    parser.add_argument("--diagnostics", default="[]", help="JSON diagnostics array")
    parser.add_argument("--provider", help="Provider name for cache events")
    parser.add_argument("--hit", type=lambda x: x.lower() == "true", default=False)
    parser.add_argument("--entries", type=int, default=0)
    parser.add_argument("--skill", help="Skill name for skill events")
    parser.add_argument("--model", default="claude", help="Model used")
    parser.add_argument("--intent", default="", help="Intent string")
    args = parser.parse_args()

    bridge = WazaaIntegration()

    if args.event == "lint":
        diagnostics = json.loads(args.diagnostics)
        count = bridge.emit_lint(file=args.file or "unknown", diagnostics=diagnostics)
        print(f"[WAZAA] lint event published to {count} subscriber(s)")

    elif args.event == "cache":
        count = bridge.emit_cache(
            provider=args.provider or "unknown",
            hit=args.hit,
            entries=args.entries,
        )
        print(f"[WAZAA] cache event published to {count} subscriber(s)")

    elif args.event == "skill":
        count = bridge.emit_skill(
            skill=args.skill or "unknown",
            model=args.model,
            intent=args.intent,
        )
        print(f"[WAZAA] skill event published to {count} subscriber(s)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
