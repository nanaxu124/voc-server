import json
from http.server import SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from .chat import llm_chat
from .config import CORS_ORIGIN, PUBLIC_MCP_TOOLS, ROOT
from .filters import common_filter_args, query_csv
from .mcp import call_voc_mcp, list_voc_tools
from .parsers import parse_intent_report, parse_kpi_report, parse_mix_report, parse_price_report


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        if CORS_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", CORS_ORIGIN)
            self.send_header("Vary", "Origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        if CORS_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", CORS_ORIGIN)
            self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type,Accept")
        self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status, message):
        self.send_json({"success": False, "error": str(message)}, status)

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/api/mcp/health":
                self.send_json({"status": "online", "supported_tools": [x.get("name") for x in list_voc_tools()]})
                return
            if parsed.path == "/api/mcp/overview_data":
                result = call_voc_mcp("voc_npi_kpi", common_filter_args(query))
                self.send_json({"success": True, "source": result["tool"], "data": parse_kpi_report(result["raw_text"]), "raw_text": result["raw_text"]})
                return
            if parsed.path == "/api/mcp/intent_data":
                result = call_voc_mcp("voc_npi_intent_details", common_filter_args(query))
                self.send_json({"success": True, "source": result["tool"], "data": parse_intent_report(result["raw_text"]), "raw_text": result["raw_text"]})
                return
            if parsed.path == "/api/mcp/mix_data":
                args = common_filter_args(query, fw_mode="list")
                for key in ("npi_sublobs", "n1_sublobs"):
                    values = query_csv(query, key)
                    if values:
                        args[key] = values
                result = call_voc_mcp("voc_npi_product_mix", args)
                self.send_json({"success": True, "source": result["tool"], "data": parse_mix_report(result["raw_text"]), "raw_text": result["raw_text"]})
                return
            if parsed.path == "/api/mcp/price_data":
                args = common_filter_args(query)
                args.pop("fw", None)
                result = call_voc_mcp("voc_npi_price_related", args)
                self.send_json({"success": True, "source": result["tool"], "data": parse_price_report(result["raw_text"]), "raw_text": result["raw_text"]})
                return
        except Exception as exc:
            self.send_error_json(503, exc)
            return
        super().do_GET()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
            if self.path == "/api/mcp/call":
                tool = data.get("tool") or data.get("name")
                if tool not in PUBLIC_MCP_TOOLS:
                    self.send_error_json(403, f"MCP tool not allowed: {tool}")
                    return
                self.send_json(call_voc_mcp(tool, data.get("arguments") or {}))
                return
            if self.path == "/api/chat":
                query = (data.get("query") or "").strip()
                if not query:
                    self.send_error_json(400, "Missing query")
                    return
                self.send_json(llm_chat(query, data.get("model") or "gemini-2.5-flash"))
                return
            self.send_error_json(404, "Not Found")
        except Exception as exc:
            self.send_error_json(500, exc)
