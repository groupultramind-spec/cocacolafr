import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace AB InBev with Coca Cola in copyright text
html = html.replace('© AB InBev', '© Coca Cola')
html = html.replace('© Ambev', '© Coca Cola') # Just in case

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Copyright text updated!")
