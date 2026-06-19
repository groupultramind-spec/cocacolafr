import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_css = """
<style>
/* Override Yellow Hamburger Menu to Red/White */
#bees-guest-variant-header-mobile-button {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #ffffff !important;
}
#bees-guest-variant-header-mobile-button svg,
#bees-guest-variant-header-mobile-button path,
#bees-guest-variant-header-mobile-button line,
#bees-guest-variant-header-mobile-button rect,
#bees-guest-variant-header-mobile-button img {
    fill: #ffffff !important;
    stroke: #ffffff !important;
    color: #ffffff !important;
    filter: brightness(0) invert(1) !important;
}
</style>
"""

# Replace the previous block if it exists
if "/* Override Yellow Hamburger Menu to Red/White */" in html:
    html = re.sub(r'<style>\s*/\* Override Yellow Hamburger Menu.*?</style>', new_css.strip(), html, flags=re.DOTALL)
else:
    html = html.replace('</head>', new_css + '\n</head>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Menu color and icon fixed!")
