import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('março 2022', 'junho 2026')
html = html.replace('mar\\u00e7o 2022', 'junho 2026')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Date updated to junho 2026")
