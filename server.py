#!/usr/bin/env python3
"""Run the VOC NPI dashboard and secure MCP proxy."""
from http.server import ThreadingHTTPServer

from voc_server.config import ALLOW_RAW_QUERY, PORT, PUBLIC_MCP_TOOLS, SSL_CTX
from voc_server.filters import common_filter_args as _common_filter_args
from voc_server.http import Handler
from voc_server.mcp import call_voc_mcp, list_voc_tools

__all__ = [
    "ALLOW_RAW_QUERY",
    "PUBLIC_MCP_TOOLS",
    "SSL_CTX",
    "_common_filter_args",
    "call_voc_mcp",
    "list_voc_tools",
]

if __name__ == "__main__":
    print(f"VOC dashboard: http://localhost:{PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
