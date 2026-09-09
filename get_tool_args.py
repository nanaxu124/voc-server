import json
import urllib.request
import ssl

def get_tools():
    url = "https://aicoach.alcnb.sbz.apple.com/chatbot-uat/mcp"
    req_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    encoded_data = json.dumps(req_data).encode("utf-8")
    req = urllib.request.Request(url, data=encoded_data, headers={
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    with urllib.request.urlopen(req, context=ctx) as response:
        return json.loads(response.read().decode("utf-8"))

tools = get_tools()
for tool in tools.get("result", {}).get("tools", []):
    if tool["name"] == "voc_npi_product_mix":
        print(json.dumps(tool, indent=2, ensure_ascii=False))
