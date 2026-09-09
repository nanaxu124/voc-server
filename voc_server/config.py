import os
import ssl
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = int(os.getenv("PORT", "8011"))
MCP_URL = os.getenv("VOC_MCP_URL", "").strip()
MCP_AUTH_TOKEN = os.getenv("VOC_MCP_AUTH_TOKEN", "").strip()
LLM_BASE_URL = os.getenv("VOC_LLM_BASE_URL", "").strip().rstrip("/")
CORS_ORIGIN = os.getenv("VOC_CORS_ORIGIN", "").strip()
CA_BUNDLE = os.getenv("VOC_CA_BUNDLE") or None
ALLOW_RAW_QUERY = os.getenv("VOC_ALLOW_RAW_QUERY", "0").lower() in {"1", "true", "yes"}
SSL_CTX = ssl.create_default_context(cafile=CA_BUNDLE)

PUBLIC_MCP_TOOLS = {
    "voc_dimensions",
    "voc_npi_kpi",
    "voc_npi_intent_details",
    "voc_npi_product_mix",
    "voc_npi_price_related",
    "search_inquiries",
    "voc_stats",
}
if ALLOW_RAW_QUERY:
    PUBLIC_MCP_TOOLS.add("query_voc")
