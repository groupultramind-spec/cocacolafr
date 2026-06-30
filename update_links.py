import os
import re

target_link = "https://wa.me/5511971730325"

files_to_update = [
    r"d:\CocaCola\index.html",
    r"d:\CocaCola\deploy\index.html",
]

for filepath in files_to_update:
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace https://wa.me/5511933684266?action=atendimento
    # Replace https://wa.me/5511933684266?action=cadastre
    # Replace https://wa.me/5511933684266
    
    content = re.sub(r"https://wa\.me/5511933684266\?action=[a-zA-Z0-9_]+", target_link, content)
    content = content.replace("https://wa.me/5511933684266", target_link)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Links updated successfully.")
