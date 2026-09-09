with open('npi_product_mix.html', 'r') as f:
    content = f.read()

import re

# Replace renderAll
old_render_all = re.search(r'function renderAll\(\) \{.*?renderPart4Tables\(\);\s*\}', content, re.DOTALL).group(0)

new_render_all = """function renderAll() {
    updateFilterButtonTexts();

    if (PRECOMPUTED_DATA) {
      renderPart2TableHTML('npiTableBody', 'npiSummaryText', PRECOMPUTED_DATA.npi_product_mix, true);
      renderPart2TableHTML('n1TableBody', 'n1SummaryText', PRECOMPUTED_DATA.n1_product_mix, false);
      renderPart4Tables(PRECOMPUTED_DATA.part4);
    }
  }"""

content = content.replace(old_render_all, new_render_all)

with open('npi_product_mix.html', 'w') as f:
    f.write(content)
