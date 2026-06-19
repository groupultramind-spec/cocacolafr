import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Disable lazyLoad in the slider settings
html = html.replace('"lazyLoad":"ondemand"', '"lazyLoad":false')

# 2. Add Preload links for the main banners to ensure instant loading
preloads = """
<link rel="preload" href="/banners/image1.png" as="image">
<link rel="preload" href="/banners/imagem2.png" as="image">
<link rel="preload" href="/banners/imagem3.png" as="image">
<link rel="preload" href="/banners/imagem4.png" as="image">
<link rel="preload" href="/images/logo.png" as="image">
"""
if '<link rel="preload" href="/banners/image1.png" as="image">' not in html:
    html = html.replace('</head>', preloads + '\n</head>')

# 3. Change loading="lazy" to loading="eager" for banners if they exist in the HTML output
html = html.replace('loading="lazy"', 'loading="eager" fetchpriority="high"')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Images optimized for instant loading!")
