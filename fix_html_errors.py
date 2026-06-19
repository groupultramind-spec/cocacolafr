import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix unclosed link tags that might cause HTML validation warnings
html = re.sub(r'<link rel="preload" href="([^"]+)" as="image">', r'<link rel="preload" href="\1" as="image" />', html)

# 2. Fix duplicate IDs across the entire HTML to satisfy the linter
ids_seen = set()
def repl(match):
    prefix = match.group(1)
    id_val = match.group(2)
    original_id = id_val
    counter = 1
    while id_val in ids_seen:
        counter += 1
        id_val = f"{original_id}_{counter}"
    ids_seen.add(id_val)
    return f'{prefix}id="{id_val}"'

# Only match HTML attributes, e.g., ' id="..."'
html = re.sub(r'(\s)id="([^"]+)"', repl, html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML errors and duplicate IDs fixed!")
