import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_css = """
<style>
/* Override Slider Blue Dot and Yellow Arrows */
button[class*="isCurrentSlide-true"], 
ul.slick-dots li.slick-active button, 
[class*="slick-active"] button,
.active-dot,
[aria-selected="true"] {
    background-color: #e31837 !important;
}

button[aria-label="Previous"], 
button[aria-label*="previous"], 
button[aria-label="Next"], 
button[aria-label*="next"],
.slick-arrow,
[class*="CarouselArrow"],
[class*="carousel-arrow"],
button.hexa--c-bsafzp {
    background-color: #e31837 !important;
    border: none !important;
}

button[aria-label="Previous"]:before, 
button[aria-label*="previous"]:before, 
button[aria-label="Next"]:before, 
button[aria-label*="next"]:before,
.slick-arrow:before {
    color: #ffffff !important;
}

button[aria-label="Previous"] svg, 
button[aria-label*="previous"] svg, 
button[aria-label="Next"] svg, 
button[aria-label*="next"] svg,
.slick-arrow svg,
[class*="CarouselArrow"] svg,
[class*="carousel-arrow"] svg,
button.hexa--c-bsafzp svg,
button.hexa--c-bsafzp path,
button.hexa--c-bsafzp rect,
button.hexa--c-bsafzp polygon,
button.hexa--c-bsafzp polyline {
    filter: brightness(0) invert(1) !important;
    fill: #ffffff !important;
}

/* Fallback for the yellow arrows if they are just divs */
div[class*="arrow"], div[class*="Arrow"] {
    background-color: #e31837 !important;
}
div[class*="arrow"] svg, div[class*="Arrow"] svg {
    filter: brightness(0) invert(1) !important;
}
</style>
"""

if "/* Override Slider Blue Dot and Yellow Arrows */" in html:
    html = re.sub(r'<style>\s*/\* Override Slider Blue Dot and Yellow Arrows.*?</style>', new_css.strip(), html, flags=re.DOTALL)
else:
    html = html.replace('</head>', new_css + '\n</head>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Slider arrows background set to RED!")
