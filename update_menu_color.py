import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

menu_css = """
<style>
/* Override Yellow Hamburger Menu to Red/White */
.is-position-sticky button:has(svg) {
    background-color: #e31837 !important;
    border: none !important;
    color: #ffffff !important;
}
.is-position-sticky button:has(svg) svg,
.is-position-sticky button:has(svg) svg path {
    fill: #ffffff !important;
    color: #ffffff !important;
}
</style>
"""

if "/* Override Yellow Hamburger Menu" not in html:
    html = html.replace('</head>', menu_css + '\n</head>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Menu color updated!")
