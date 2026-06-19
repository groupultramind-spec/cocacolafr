import json
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace social links
html = html.replace('https://www.instagram.com/bees.brasil', 'https://www.instagram.com/cocacola_br/')
html = html.replace('https://www.facebook.com/parceirobees', 'https://www.facebook.com/cocacolabr')

# Update the JSON if needed (the above simple replacements should catch both JSON and HTML strings if they are exact)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Footer social links updated!")
