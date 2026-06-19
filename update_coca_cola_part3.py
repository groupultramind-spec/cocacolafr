import json
import re
import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    # 1. Update the 4th icon to coca-cola-favicon.ico
    def fix_4th_icon(node):
        if isinstance(node, dict):
            if node.get("name") == "number-items-image-3" and "attributes" in node:
                node["attributes"]["src"] = "/images/coca-cola-favicon.ico"
            for k, v in node.items():
                fix_4th_icon(v)
        elif isinstance(node, list):
            for item in node:
                fix_4th_icon(item)

    fix_4th_icon(data)

    # 2. Update footer app store links and any 'href' in badges
    def fix_app_store_links(node):
        if isinstance(node, dict):
            # If it's a badgesSection or badge item
            if "href" in node and isinstance(node["href"], str) and ("play.google.com" in node["href"] or "apps.apple.com" in node["href"]):
                node["href"] = "https://wa.me/"
            for k, v in node.items():
                fix_app_store_links(v)
        elif isinstance(node, list):
            for item in node:
                fix_app_store_links(item)

    fix_app_store_links(data)

    # 3. Update all image src attributes to point to local versions if they exist
    local_images = [
        "business-benefits_boxes-n-laptop.png",
        "cesta.png",
        "coca-cola-favicon.ico",
        "how-it-works-1_phone.png",
        "how-it-works-2_truck.png",
        "logo.png",
        "mobile-download_phone.png",
        "need-help_user.png",
        "your-business-more-easy.png"
    ]
    
    def replace_local_images(node):
        if isinstance(node, dict):
            if "src" in node and isinstance(node["src"], str):
                for img in local_images:
                    if img in node["src"] and not node["src"].startswith("/images/"):
                        node["src"] = "/images/" + img
            for k, v in node.items():
                replace_local_images(v)
        elif isinstance(node, list):
            for item in node:
                replace_local_images(item)

    replace_local_images(data)
    
    new_json = json.dumps(data, separators=(',', ':'))
    new_html = html[:match.start(1)] + new_json + html[match.end(1):]
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Successfully fixed 4th icon, store links, and local images.")
else:
    print("Could not find __NEXT_DATA__")
