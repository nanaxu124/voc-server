import json
import urllib.request

from .config import LLM_BASE_URL, SSL_CTX
from .mcp import call_voc_mcp


def llm_chat(query, model):
    lowered = query.lower()
    tool = "voc_npi_kpi"
    if any(key in lowered for key in ("price", "价格", "差价")):
        tool = "voc_npi_price_related"
    elif any(key in lowered for key in ("intent", "意图", "问题", "咨询")):
        tool = "voc_npi_intent_details"

    context = call_voc_mcp(tool, {"product_type": "iPhone"})["raw_text"]
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是 VOC 数据分析助手。只基于给定数据回答；数据不足时明确说明。\n\n" + context[:20000],
            },
            {"role": "user", "content": query},
        ],
        "max_tokens": 1600,
    }
    endpoint = f"{LLM_BASE_URL}/{model}/v1/chat/completions"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, context=SSL_CTX, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
    answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"success": True, "answer": answer, "model_used": model, "voc_tool": tool}
