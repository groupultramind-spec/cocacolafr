with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace invalid "@media {" with "@media all {"
html = html.replace('@media {', '@media all {')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed @media { syntax errors!")
