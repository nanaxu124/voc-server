import json
import urllib.request

from .config import MCP_AUTH_TOKEN, MCP_URL, SSL_CTX


def rpc(method, params=None):
    if not MCP_URL:
        raise RuntimeError("VOC_MCP_URL is not configured")
    payload = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        payload["params"] = params
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if MCP_AUTH_TOKEN:
        headers["X-MCP-Auth"] = MCP_AUTH_TOKEN
    request = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
    )
    with urllib.request.urlopen(request, context=SSL_CTX, timeout=30) as response:
        raw = response.read().decode("utf-8")
    events = [line[5:].strip() for line in raw.splitlines() if line.startswith("data:")]
    data = json.loads(events[-1] if events else raw)
    if data.get("error"):
        error = data["error"]
        raise RuntimeError(error.get("message", str(error)))
    return data.get("result", {})


def list_voc_tools():
    return rpc("tools/list").get("tools", [])


def call_voc_mcp(name, arguments=None):
    result = rpc("tools/call", {"name": name, "arguments": arguments or {}})
    texts = [
        item.get("text", "")
        for item in result.get("content", [])
        if item.get("type") == "text"
    ]
    return {
        "success": True,
        "tool": name,
        "raw_text": "\n".join(texts),
        "raw_result": result,
    }
