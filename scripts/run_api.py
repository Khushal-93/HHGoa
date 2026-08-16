import sys
import argparse
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Run HHGoa RAG Retrieval API Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    print(f"Starting HHGoa Retrieval API on http://{args.host}:{args.port}...")
    uvicorn.run("rag.api:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
