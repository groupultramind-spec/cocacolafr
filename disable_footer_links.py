import json
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace specific links in the footer JSON with javascript:void(0) to disable them
html = html.replace('"href":"https://www.bees.com/pt-br"', '"href":"javascript:void(0)"')
html = html.replace('"href":"/privacy-policy"', '"href":"javascript:void(0)"')
html = html.replace('"href":"/terms-and-conditions"', '"href":"javascript:void(0)"')

# Also replace them in case the JSON is formatted with spaces
html = html.replace('"href": "https://www.bees.com/pt-br"', '"href": "javascript:void(0)"')
html = html.replace('"href": "/privacy-policy"', '"href": "javascript:void(0)"')
html = html.replace('"href": "/terms-and-conditions"', '"href": "javascript:void(0)"')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Links disabled successfully!")
