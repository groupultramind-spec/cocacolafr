import json
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    def restore_globe(node):
        if isinstance(node, dict):
            if node.get("name") == "number-items-image-3" and "attributes" in node:
                node["attributes"]["src"] = "/images/numbers_countries_globe.png"
            for k, v in node.items():
                restore_globe(v)
        elif isinstance(node, list):
            for item in node:
                restore_globe(item)

    restore_globe(data)
    
    new_json = json.dumps(data, separators=(',', ':'))
    new_html = html[:match.start(1)] + new_json + html[match.end(1):]
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Successfully restored the globe icon.")
else:
    print("Could not find __NEXT_DATA__")
