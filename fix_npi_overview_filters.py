with open('npi_overview.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_str = """        const params = new URLSearchParams();
        if (selectedFW) params.append('fw', selectedFW.split(',')[0]);
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);"""

new_str = """        const params = new URLSearchParams();
        const fwAll = document.getElementById('fw-all');
        if (!fwAll || !fwAll.checked) {
            if (selectedFW) params.append('fw', selectedFW.split(',')[0]);
        }
        const dateAll = document.getElementById('date-all');
        if (!dateAll || !dateAll.checked) {
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);
        }"""

content = content.replace(old_str, new_str)
with open('npi_overview.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Replaced!")
