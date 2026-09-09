with open('npi_product_mix.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_str = """        const liveRawData = [];
        let dt = '2025-09-10'; // default

        for (const [prodName, list] of Object.entries(prodMap)) {
            liveRawData.push({
                type: 'iPhone',
                prodName: prodName,
                date: dt,
                mixList: list
            });
        }"""

new_str = """        const liveRawData = [];
        for (const [prodName, list] of Object.entries(prodMap)) {
            let dt = '2025-09-10';
            if (n1Products.includes(prodName)) {
                dt = '2024-09-10';
            }
            liveRawData.push({
                type: 'iPhone',
                prodName: prodName,
                date: dt,
                mixList: list,
                isLive: true
            });
        }"""

content = content.replace(old_str, new_str)

old_str2 = """    const matchedRecords = RAW_IPHONE_DATA.filter(r => {
      const d = r.date || '';
      if (!d.startsWith(yearPrefix)) return false;
      if (allowedDates.size > 0 && !allowedDates.has(d)) return false;

      if (allowedFws.size > 0) {
        const fws = (r.intentDetailList || []).map(x => `${x.fy}${x.fq}${x.fw}`);
        if (!fws.some(f => allowedFws.has(f))) return false;
      }
      return true;
    });"""

new_str2 = """    const matchedRecords = RAW_IPHONE_DATA.filter(r => {
      if (r.isLive) return true;
      const d = r.date || '';
      if (!d.startsWith(yearPrefix)) return false;
      if (allowedDates.size > 0 && !allowedDates.has(d)) return false;

      if (allowedFws.size > 0) {
        const fws = (r.intentDetailList || []).map(x => `${x.fy}${x.fq}${x.fw}`);
        if (!fws.some(f => allowedFws.has(f))) return false;
      }
      return true;
    });"""

content = content.replace(old_str2, new_str2)

with open('npi_product_mix.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Replaced!")
