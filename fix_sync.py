with open('npi_product_mix.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

old_sync = re.search(r'async function syncAndRender\(\) \{.*?RAW_IPHONE_DATA = liveRawData;\s*renderAll\(\);\s*\} catch \(err\) \{\s*console\.warn\(\'\[syncAndRender\]\', err\);\s*renderAll\(\);\s*\}\s*\}', content, re.DOTALL).group(0)

new_sync = """let PRECOMPUTED_DATA = null;

  async function syncAndRender() {
      try {
        // Build query string
        const params = new URLSearchParams();
        
        // Date
        const dates = Array.from(state.selectedDates).sort();
        if (dates.length > 0) {
            params.append('date_from', dates[0]);
            params.append('date_to', dates[dates.length - 1]);
        }
        
        // FW
        const fws = Array.from(state.selectedFws).sort();
        if (fws.length > 0) {
            params.append('fw', fws.join(','));
        }
        
        // NPI Sub LOB
        const npiSub = Array.from(state.selectedNpiSubLobs);
        if (npiSub.length > 0) {
            params.append('npi_sublobs', npiSub.join(','));
        }
        
        // N-1 Sub LOB
        const n1Sub = Array.from(state.selectedN1SubLobs);
        if (n1Sub.length > 0) {
            params.append('n1_sublobs', n1Sub.join(','));
        }
        
        const qs = params.toString();
        const url = qs ? `./api/mcp/mix_data?${qs}` : `./api/mcp/mix_data`;
        
        const res = await fetch(url, {headers: {'X-MCP-Auth': 'voc_proxy_secret_123'}});
        if (!res.ok) {
            renderAll();
            return;
        }
        const json = await res.json();
        if (!json.success || !json.data) {
            renderAll();
            return;
        }

        PRECOMPUTED_DATA = json.data;
        renderAll();
      } catch (err) {
        console.warn('[syncAndRender]', err);
        renderAll();
      }
    }"""

content = content.replace(old_sync, new_sync)

with open('npi_product_mix.html', 'w', encoding='utf-8') as f:
    f.write(content)
