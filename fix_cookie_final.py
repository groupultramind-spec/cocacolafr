import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the button color to red with white text
html = html.replace('background-color: #ffeb00;', 'background-color: #e31837;')
html = html.replace('color: #000000;', 'color: #ffffff;')
html = html.replace('background-color: #e6d400;', 'background-color: #b3122b;')

# Remove the extra Aceitar e Fechar button
to_remove = """    <button class="custom-cookie-btn" onclick="document.getElementById('customCookieBanner').style.display='none'">Aceitar e Fechar</button>
</div>"""
html = html.replace(to_remove, '')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Cookie banner fixed!")
