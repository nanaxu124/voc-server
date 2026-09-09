#!/usr/bin/env python3
"""Print the configured MCP tool catalog without disabling TLS verification."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server import list_voc_tools  # noqa: E402


def main() -> int:
    tools = list_voc_tools()
    print(json.dumps(tools, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
