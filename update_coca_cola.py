import json
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    # 1. Update banners
    banner_images = [
        "/banners/image1.png",
        "/banners/imagem2.png",
        "/banners/imagem3.png",
        "/banners/imagem4.png"
    ]
    banner_idx = 0
    
    def walk_banners(node):
        global banner_idx
        if isinstance(node, dict):
            # Check if this is an Image block and inside a slider or we can just replace all big banners
            if node.get("blockType") == "Image" and "attributes" in node and "src" in node["attributes"]:
                src = node["attributes"]["src"]
                # The guest banners seem to have "Slide" in the alt text or specific height
                alt = node["attributes"].get("alt", "")
                if "Slide" in alt or "banner" in src.lower() or node["attributes"].get("height") == 465:
                    if banner_idx < len(banner_images):
                        node["attributes"]["src"] = banner_images[banner_idx]
                        node["attributes"]["optimizationParams"] = {} # Disable Next.js optimization for local images
                        banner_idx += 1
            for k, v in node.items():
                walk_banners(v)
        elif isinstance(node, list):
            for item in node:
                walk_banners(item)
                
    walk_banners(data)

    # 2. Update Header buttons
    def update_buttons(node):
        if isinstance(node, dict):
            # Change "Entrar" to "Ir para atendimento"
            if node.get("text") == "Entrar":
                node["text"] = "Ir para atendimento"
            if node.get("buttonLabel") == "Entrar":
                node["buttonLabel"] = "Ir para atendimento"
            
            # Hide "Cadastre-se" by adding a display-none class or just clearing the text
            if node.get("text") == "Cadastre-se":
                node["text"] = ""
                # try to add a hidden class
                if "classes" in node:
                    node["classes"] = node.get("classes", "") + " is-hidden"
            if node.get("buttonLabel") == "Cadastre-se":
                node["buttonLabel"] = ""
            
            for k, v in node.items():
                update_buttons(v)
        elif isinstance(node, list):
            # We can also completely remove the block if it's the "Cadastre-se" button
            items_to_remove = []
            for item in node:
                if isinstance(item, dict):
                    if item.get("text") == "Cadastre-se" or item.get("buttonLabel") == "Cadastre-se" or (item.get("attributes", {}).get("buttonLabel") == "Cadastre-se"):
                        items_to_remove.append(item)
                update_buttons(item)
            for item in items_to_remove:
                node.remove(item)

    update_buttons(data)
    
    new_json = json.dumps(data, separators=(',', ':'))
    new_html = html[:match.start(1)] + new_json + html[match.end(1):]
    
    # Add custom CSS for the red header and white text
    custom_css = """
<style>
  /* Coca-Cola Header overrides */
  #home_guest_header_wrapper_pt_BR,
  #home_guest_header_wrapper_pt_BR > div,
  #home_guest_header_wrapper_pt_BR .is-primary-background {
    background-color: #F40009 !important;
  }
  #home_guest_header_wrapper_pt_BR span,
  #home_guest_header_wrapper_pt_BR p,
  #home_guest_header_wrapper_pt_BR a,
  #home_guest_header_wrapper_pt_BR div.bees-text {
    color: #FFFFFF !important;
  }
  /* Fix specific texts like "Como funciona?" */
  #home_guest_header_wrapper_pt_BR .is-text-black {
    color: #FFFFFF !important;
  }
  #home_guest_header_wrapper_pt_BR svg,
  #home_guest_header_wrapper_pt_BR svg path {
    fill: #FFFFFF !important;
  }
  
  /* Make sure the remaining button looks right */
  #home_guest_header_wrapper_pt_BR .bees-button {
    background-color: #FFFFFF !important;
    color: #F40009 !important;
    border: 1px solid #FFFFFF !important;
  }
  #home_guest_header_wrapper_pt_BR .bees-button span {
    color: #F40009 !important;
  }
</style>
</head>
"""
    new_html = new_html.replace('</head>', custom_css)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Successfully updated index.html with Coca-Cola styles, buttons, and banners.")
else:
    print("Could not find __NEXT_DATA__")
