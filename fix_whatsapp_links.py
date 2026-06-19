import json
import re

files_to_fix = ['index.html', 'deploy/index.html']

for file_path in files_to_fix:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Replace string literal
        html = html.replace('/redirect_whatsapp', 'https://wa.me/5511999999999')
        
        # Replace inside __NEXT_DATA__
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                def replace_links(node):
                    if isinstance(node, dict):
                        for k, v in node.items():
                            if isinstance(v, str) and v == "/redirect_whatsapp":
                                node[k] = "https://wa.me/5511999999999"
                            else:
                                replace_links(v)
                    elif isinstance(node, list):
                        for item in node:
                            replace_links(item)
                
                replace_links(data)
                new_json = json.dumps(data, separators=(',', ':'))
                html = html[:match.start(1)] + new_json + html[match.end(1):]
            except Exception as e:
                print(f"Error parsing JSON in {file_path}: {e}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"Updated WhatsApp links successfully in {file_path}")
    except Exception as e:
        print(f"Could not update {file_path}: {e}")
