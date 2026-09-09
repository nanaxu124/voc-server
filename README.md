# VOC NPI Dashboard Server

Runnable NPI VOC dashboard plus a small Python proxy for the VOC MCP server. The browser talks only to this service; MCP credentials stay server-side.

## Layout

```text
.
├── server.py                  # process entrypoint
├── voc_server/
│   ├── config.py              # fixed service endpoints, TLS, allowlist
│   ├── filters.py             # dashboard filter -> MCP args
│   ├── mcp.py                 # tools/list + tools/call
│   ├── parsers.py             # text/TSV normalization
│   ├── chat.py                # MCP-grounded LLM chat
│   └── http.py                # REST/static HTTP handler
├── mcp_client.js
├── index.html / app.js / styles.css
├── dashboard.js
├── overview.js / intent.js / mix.js / price.js
├── npi_overview.html
├── npi_intent_details.html
├── npi_product_mix.html
├── npi_price_related.html
├── scripts/inspect_mcp_tools.py
└── tests/test_server.py
```

Prototype-only artifacts from the uploaded working directory (`fix_*.py`, `patch_*.py`, logs, `__pycache__`, chromedriver and nested archives) are intentionally not tracked.

## Run

Python 3.10+ is enough; there are no third-party Python dependencies.

The original internal endpoints are hardcoded in `voc_server/config.py`:

```text
MCP: https://aicoach.alcnb.sbz.apple.com/chatbot-uat/mcp
LLM: https://i-build.alcnb.shld.apple.com/llm/{model}/v1/chat/completions
```

Normally you can start the service directly:

```bash
python server.py
```

Only set the optional server-side MCP token when the MCP service actually requires one:

```bash
export VOC_MCP_AUTH_TOKEN='...'
python server.py
```

Open `http://localhost:8011/`.

For an internal/private CA, keep verification enabled and point to the trusted PEM bundle:

```bash
export VOC_CA_BUNDLE='/path/to/company-ca.pem'
```

## P0 safety and correctness

- MCP and LLM service addresses keep the original hardcoded internal endpoints.
- TLS certificate verification is enabled for MCP and LLM traffic.
- Optional MCP credentials come from `VOC_MCP_AUTH_TOKEN`; no browser file contains the credential.
- CORS is same-origin by default and can be explicitly configured with `VOC_CORS_ORIGIN`.
- `/api/mcp/call` has an allowlist. `query_voc` is disabled unless `VOC_ALLOW_RAW_QUERY=1` is explicitly set.
- Dashboard date filters are forwarded to the MCP tools.
- A single FW stays a scalar for backward compatibility; multiple FWs are forwarded as an array rather than silently truncating to the first value.
- Product Mix sends FW as an array and forwards NPI/N-1 sub-LOB selections.
- Product Mix no longer bypasses filters for `isLive` records, and no fake dates are injected in the browser.
- Browser-side SQL and the unauthenticated shutdown behavior from the prototype are removed.

## Checks

```bash
python -m unittest discover -s tests -v
python -m py_compile server.py voc_server/*.py scripts/inspect_mcp_tools.py
for f in *.js; do node --check "$f"; done
```

To inspect the live MCP tool catalog with verified TLS:

```bash
python scripts/inspect_mcp_tools.py
```
