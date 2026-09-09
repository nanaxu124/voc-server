with open('npi_overview.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find index of "// 页面加载自动初始化"
start_idx = -1
for i, line in enumerate(lines):
    if "// 页面加载自动初始化" in line:
        start_idx = i
        break

if start_idx != -1:
    lines = lines[:start_idx]
    
    new_code = """    // 页面加载自动初始化
    window.addEventListener('DOMContentLoaded', () => {
      initFilters();
      recalculateAndRender();
      syncWithLiveVOCMCP();
    });

    async function syncWithLiveVOCMCP() {
      try {
        const selectedFW = Array.from(document.querySelectorAll('#drop-fw .opt-item:checked')).map(i => i.value).join(',');
        let selectedDates = Array.from(document.querySelectorAll('#drop-date .opt-item:checked')).map(i => i.value).sort();
        selectedDates = selectedDates.map(d => d.replace(/\\//g, '-'));
        let dateFrom = '', dateTo = '';
        if (selectedDates.length > 0) {
          dateFrom = selectedDates[0];
          dateTo = selectedDates[selectedDates.length - 1];
        }

        const params = new URLSearchParams();
        if (selectedFW) params.append('fw', selectedFW.split(',')[0]);
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);
        const res = await fetch(`./api/mcp/overview_data?${params.toString()}`, {headers: {'X-MCP-Auth': 'voc_proxy_secret_123'}});
        if (!res.ok) return;
        const json = await res.json();
        if (!json.success || !json.data) return;
        const live = json.data;
        const kpis = live.kpis;

        // Update UI
        if (kpis.customers) {
          document.getElementById('kpi-cust-npi').textContent = Number(kpis.customers.npi).toLocaleString();
          document.getElementById('kpi-cust-n1').textContent = Number(kpis.customers.n1).toLocaleString();
          const elCustLol = document.getElementById('kpi-cust-lol');
          if (elCustLol) {
            const lolStr = kpis.customers.lol;
            elCustLol.textContent = (lolStr.startsWith('+') || lolStr.startsWith('-')) ? lolStr : `+${lolStr}`;
            elCustLol.className = `kpi-number-lol ${parseFloat(lolStr) >= 0 ? 'lol-positive' : 'lol-negative'}`;
          }
        }
        if (kpis.inquiries) {
          document.getElementById('kpi-inq-npi').textContent = Number(kpis.inquiries.npi).toLocaleString();
          document.getElementById('kpi-inq-n1').textContent = Number(kpis.inquiries.n1).toLocaleString();
          const elInqLol = document.getElementById('kpi-inq-lol');
          if (elInqLol) {
            const lolStr = kpis.inquiries.lol;
            elInqLol.textContent = (lolStr.startsWith('+') || lolStr.startsWith('-')) ? lolStr : `+${lolStr}`;
            elInqLol.className = `kpi-number-lol ${parseFloat(lolStr) >= 0 ? 'lol-positive' : 'lol-negative'}`;
          }
        }
        if (kpis.cvr) {
          document.getElementById('kpi-cvr-npi').textContent = kpis.cvr.npi;
          document.getElementById('kpi-cvr-n1').textContent = kpis.cvr.n1;
          const elCvrLol = document.getElementById('kpi-cvr-lol');
          if (elCvrLol) {
            const lolStr = kpis.cvr.lol;
            elCvrLol.textContent = (lolStr.startsWith('+') || lolStr.startsWith('-')) ? lolStr : `+${lolStr}`;
            elCvrLol.className = `kpi-number-lol ${parseFloat(lolStr) >= 0 ? 'lol-positive' : 'lol-negative'}`;
          }
        }

        // Update Charts
        const cvrAvg = parseFloat(kpis.cvr ? kpis.cvr.npi : 4.1) || 4.1;
        if (live.program && live.program.length > 0) {
          renderSpecMatrix(live.program, 'program-axis-container', 'program-bars-container', 'program-dots-container', 'program-avg-header', 'program-avg-line', cvrAvg);
        }
        if (live.feature && live.feature.length > 0) {
          renderSpecMatrix(live.feature, 'feature-axis-container', 'feature-bars-container', 'feature-dots-container', 'feature-avg-header', 'feature-avg-line', cvrAvg);
        }
        if (live.trend && live.trend.length > 0) {
          const dates = live.trend.map(t => t.date);
          const npiVals = live.trend.map(t => t.npi);
          const n1Vals = live.trend.map(t => t.n1);
          renderTrendChart(dates, npiVals, n1Vals);
        }
        const tsEl = document.getElementById('data-timestamp');
        if (tsEl) {
          tsEl.textContent = `Data as of ${live.date_timestamp || '2026/08/25'} (VOC 实时取数)`;
        }
      } catch (err) {
        console.warn('[syncWithLiveVOCMCP]', err);
      }
    }
</script>
</body>
</html>
"""
    lines.append(new_code)
    
    with open('npi_overview.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Fixed npi_overview.html")
else:
    print("Could not find '// 页面加载自动初始化'")
