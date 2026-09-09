with open('npi_product_mix.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_str = """        const liveRawData = [];
        for (const [prodName, list] of Object.entries(prodMap)) {
            let dt = '2025-09-10';
            if (n1Products.includes(prodName)) {"""

new_str = """        const liveRawData = [];
        const n1Set = ['iPhone 16', 'iPhone 16 Plus', 'iPhone 16 Pro', 'iPhone 16 Pro Max'];
        for (const [prodName, list] of Object.entries(prodMap)) {
            let dt = '2025-09-10';
            if (n1Set.includes(prodName)) {"""

content = content.replace(old_str, new_str)

with open('npi_product_mix.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Replaced!")
