import json
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace in standard HTML
html = html.replace('https://wa.me/', '/redirect_whatsapp')

# Replace in NEXT_DATA if any
match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    def replace_links(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str) and "wa.me" in v:
                    node[k] = "/redirect_whatsapp"
                else:
                    replace_links(v)
        elif isinstance(node, list):
            for item in node:
                replace_links(item)

    replace_links(data)
    new_json = json.dumps(data, separators=(',', ':'))
    html = html[:match.start(1)] + new_json + html[match.end(1):]
    
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
    
print("Updated WhatsApp links to /redirect_whatsapp")
