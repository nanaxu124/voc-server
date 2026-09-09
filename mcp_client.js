/**
 * VOC MCP Client for NPI Dashboard
 * Uses the local voc-server proxy; the browser never holds MCP credentials.
 */

class VOCMCPClient {
  constructor(baseUrl = '') {
    if (baseUrl) {
      this.baseUrl = baseUrl.replace(/\/$/, '');
    } else if (typeof window !== 'undefined' && window.location.protocol !== 'file:') {
      this.baseUrl = window.location.origin;
    } else {
      this.baseUrl = 'http://127.0.0.1:8011';
    }
    this.isConnected = false;
    this.latencyMs = 0;
  }

  async checkHealth() {
    const t0 = performance.now();
    try {
      const res = await fetch(`${this.baseUrl}/api/mcp/health`);
      if (res.ok) {
        const data = await res.json();
        this.latencyMs = Math.round(performance.now() - t0);
        this.isConnected = data.status === 'online';
        return { ok: true, data, latency: this.latencyMs };
      }
    } catch (e) {
      console.warn('[MCP] Health check failed:', e);
    }
    this.isConnected = false;
    return { ok: false, latency: 0 };
  }

  async call(toolName, args = {}) {
    const t0 = performance.now();
    const res = await fetch(`${this.baseUrl}/api/mcp/call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool: toolName, arguments: args })
    });
    const duration = Math.round(performance.now() - t0);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    const json = await res.json();
    return {
      tool: toolName,
      rawText: json.raw_text || '',
      durationMs: duration
    };
  }

  // Parse Markdown/TSV tables from VOC MCP output
  parseTSV(tsvText) {
    if (!tsvText) return [];
    const lines = tsvText.trim().split('\n').filter(l => l.trim().length > 0 && !l.startsWith('##'));
    if (lines.length < 2) return [];
    const headers = lines[0].split('\t').map(h => h.trim());
    const rows = [];
    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split('\t');
      const row = {};
      headers.forEach((h, idx) => {
        row[h] = cols[idx] !== undefined ? cols[idx].trim() : '';
      });
      rows.push(row);
    }
    return rows;
  }

  // Parse Section-based Markdown (e.g., voc_npi_kpi)
  parseKPIMarkdown(text) {
    const sections = {};
    const lines = text.split('\n');
    let currentSection = 'General';
    let currentLines = [];

    for (const line of lines) {
      if (line.startsWith('## ')) {
        if (currentLines.length > 0) {
          sections[currentSection] = currentLines.join('\n');
          currentLines = [];
        }
        currentSection = line.replace('## ', '').trim();
      } else {
        currentLines.push(line);
      }
    }
    if (currentLines.length > 0) {
      sections[currentSection] = currentLines.join('\n');
    }

    // Extract core KPIs
    const kpiSummary = {};
    for (const [secName, secContent] of Object.entries(sections)) {
      if (secName.includes('Report') || secName.includes('KPI')) {
        const rows = this.parseTSV(secContent);
        rows.forEach(r => {
          if (r.KPI) {
            kpiSummary[r.KPI] = {
              npi: r.NPI,
              n1: r['N-1'],
              lol: r.LoL
            };
          }
        });
      }
    }

    return { sections, kpiSummary };
  }

  // 1. Get KPI
  async getKPI(productType = 'iPhone', fw = null, dates = null) {
    const args = { product_type: productType };
    if (fw) args.fw = fw;
    if (dates && dates.length > 0) {
      args.date_from = dates[0];
      args.date_to = dates[dates.length - 1];
    }
    const res = await this.call('voc_npi_kpi', args);
    const parsed = this.parseKPIMarkdown(res.rawText);
    return { ...res, parsed };
  }

  // 2. Get Dimensions
  async getDimensions(prodType = 'iPhone') {
    const res = await this.call('voc_dimensions', { prod_type: prodType });
    return res;
  }

  // 3. Search inquiries
  async searchInquiries(keyword = '', prodType = 'iPhone', limit = 20) {
    const args = { prod_type: prodType, limit };
    if (keyword) args.keyword = keyword;
    const res = await this.call('search_inquiries', args);
    const rows = this.parseTSV(res.rawText);
    return { ...res, rows };
  }

  // 4. Price related
  async getPriceRelated(productType = 'iPhone', dateFrom = '2025-09-10', dateTo = '2025-09-12') {
    const res = await this.call('voc_npi_price_related', {
      product_type: productType,
      date_from: dateFrom,
      date_to: dateTo
    });
    return res;
  }

  // 5. Product mix through the business endpoint (no browser-side SQL)
  async getProductMix(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') query.set(key, value);
    });
    const t0 = performance.now();
    const suffix = query.toString() ? `?${query.toString()}` : '';
    const res = await fetch(`${this.baseUrl}/api/mcp/mix_data${suffix}`);
    const durationMs = Math.round(performance.now() - t0);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    const json = await res.json();
    return { ...json, durationMs };
  }

  // 6. Direct LLM Chat with VOC RAG
  async chatWithLLM(query, model = 'gemini-3.1-pro-preview') {
    const res = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, model })
    });
    if (!res.ok) {
      throw new Error(`Chat API error HTTP ${res.status}`);
    }
    return await res.json();
  }
}

// Global instance
window.vocMCP = new VOCMCPClient();
