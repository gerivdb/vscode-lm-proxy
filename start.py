#!/usr/bin/env python
"""
LM Hack Proxy Startup Script
Simple launcher for the LM Hack Proxy server
"""

import logging
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    """Main startup function"""
    print("[Launch] Starting LM Hack Proxy...")

    # Set basic environment variables if not set
    if "LM_HACK_PORT" not in os.environ:
        os.environ["LM_HACK_PORT"] = "4000"
    if "LM_HACK_HOST" not in os.environ:
        os.environ["LM_HACK_HOST"] = "0.0.0.0"

    port = os.environ.get("LM_HACK_PORT", "4000")
    host = os.environ.get("LM_HACK_HOST", "0.0.0.0")

    print(f"📍 Server will start on http://{host}:{port}")
    print(f"📖 API documentation: http://{host}:{port}/docs")
    print(f"🔍 Health check: http://{host}:{port}/health")
    print()

    try:
        # Import and run server
        import uvicorn
        from server import app

        print("[OK] Server components loaded successfully")
        print("[Target] Ready to serve LLM orchestration requests!")
        print()

        # Start server
        uvicorn.run(
            "server:app", host=host, port=int(port), reload=True, log_level="info"
        )

    except ImportError as e:
        print(f"[X] Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    except Exception as e:
        print(f"[X] Startup failed: {e}")
        logging.exception("Server startup error")
        sys.exit(1)


if __name__ == "__main__":
    main()
