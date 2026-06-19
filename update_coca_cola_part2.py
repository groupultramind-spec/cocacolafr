import json
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    # 1. Replace "BEES" and "Bees" with "Coca Cola" in textual properties
    def replace_text(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ["text", "title", "description", "alt", "buttonLabel", "link_label", "buttonName"]:
                    if isinstance(v, str):
                        v = v.replace("BEES", "Coca Cola").replace("Bees", "Coca Cola")
                        node[k] = v
                else:
                    replace_text(v)
            
            # 2. Replace icons in the numbers section
            if node.get("name") == "number-items-image-0":
                if "attributes" in node:
                    node["attributes"]["src"] = "/images/need-help_user.png"
            elif node.get("name") == "number-items-image-1":
                if "attributes" in node:
                    node["attributes"]["src"] = "/images/how-it-works-2_truck.png"
            elif node.get("name") == "number-items-image-2":
                if "attributes" in node:
                    node["attributes"]["src"] = "/images/cesta.png"
            elif node.get("name") == "number-items-image-3":
                if "attributes" in node:
                    node["attributes"]["src"] = "/images/logo.png"
            
            # 3. Replace App Store links with WhatsApp link
            if node.get("blockType") == "DownloadBadge":
                if "attributes" in node:
                    node["attributes"]["downloadLink"] = "https://wa.me/"
                    
        elif isinstance(node, list):
            for item in node:
                replace_text(item)

    replace_text(data)

    # 4. Replace favicon and main logos
    def replace_logos(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "icon" and isinstance(v, str) and "favicon" in v:
                    node[k] = "/images/coca-cola-favicon.ico"
                elif k == "logo" and isinstance(v, dict) and "src" in v:
                    v["src"] = "/images/logo.png"
                elif k == "logo" and isinstance(v, str):
                    node[k] = "/images/logo.png"
                replace_logos(v)
        elif isinstance(node, list):
            for item in node:
                replace_logos(item)

    replace_logos(data)
    
    # Dump the json back
    new_json = json.dumps(data, separators=(',', ':'))
    new_html = html[:match.start(1)] + new_json + html[match.end(1):]
    
    # Replace any stray "BEES" in standard HTML text just in case (e.g. server rendered text)
    # Be careful not to replace class names like "bees-col"
    new_html = new_html.replace('>BEES<', '>Coca Cola<')
    new_html = new_html.replace(' No BEES,', ' Na Coca Cola,')
    new_html = new_html.replace(' o BEES', ' a Coca Cola')
    new_html = new_html.replace(' O BEES', ' A Coca Cola')
    new_html = new_html.replace(' no BEES', ' na Coca Cola')
    new_html = new_html.replace(' No BEES ', ' Na Coca Cola ')
    
    # Save back
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Successfully updated text, icons, and store links.")
else:
    print("Could not find __NEXT_DATA__")
