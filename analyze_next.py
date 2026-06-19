import json
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    def find_images(d, path=""):
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, str) and ('.png' in v or '.jpg' in v or '.webp' in v):
                    print(f"Found image at {path}.{k}: {v}")
                if isinstance(v, (dict, list)):
                    find_images(v, path + "." + k)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                if isinstance(item, (dict, list)):
                    find_images(item, path + f"[{i}]")

    find_images(data)
else:
    print("No __NEXT_DATA__ found")
