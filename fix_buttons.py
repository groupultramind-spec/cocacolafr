import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_css = """
<style>
/* Override Button Colors and Links */
a[href="/login"] button, button.is-primary {
    background-color: #e31837 !important;
    border-color: #e31837 !important;
    color: #ffffff !important;
}
.slick-prev:before, .slick-next:before {
    color: #e31837 !important;
}
.slick-arrow {
    background-color: transparent !important;
}
.slick-arrow:before {
    color: #e31837 !important;
}
</style>
"""

if "/* Override Button Colors and Links */" in html:
    html = re.sub(r'<style>\s*/\* Override Button Colors and Links.*?</style>', new_css.strip(), html, flags=re.DOTALL)
else:
    html = html.replace('</head>', new_css + '\n</head>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Buttons fixed!")
