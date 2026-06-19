import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace javascript:void(0) with # to avoid React security error
html = html.replace('"href":"javascript:void(0)"', '"href":"#"')
html = html.replace('"href": "javascript:void(0)"', '"href": "#"')

# Also remove React's error string if it somehow got embedded
html = html.replace("javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')", "#")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Links set to #!")
