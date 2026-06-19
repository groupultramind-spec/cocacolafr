import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Viewport (Disable Zoom)
html = re.sub(
    r'<meta name="viewport" content="width=device-width" data-next-head="" />',
    r'<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" data-next-head="" />',
    html
)

# 2. Add Security CSS and JS
security_tags = """
<style>
/* CSS Anti-Copy & Anti-Drag */
body, html {
    -webkit-touch-callout: none;
    -webkit-user-select: none; 
    -khtml-user-select: none; 
    -moz-user-select: none; 
    -ms-user-select: none; 
    user-select: none; 
}
img {
    -webkit-user-drag: none;
    -khtml-user-drag: none;
    -moz-user-drag: none;
    -o-user-drag: none;
    user-drag: none;
    pointer-events: auto; /* ensure clicks still work */
}
</style>
<script>
/* JS Encryption & Anti-Copy System */
(function(){
    document.addEventListener('contextmenu', function(e) { e.preventDefault(); return false; });
    document.addEventListener('dragstart', function(e) { e.preventDefault(); return false; });
    document.addEventListener('copy', function(e) { e.preventDefault(); return false; });
    document.addEventListener('cut', function(e) { e.preventDefault(); return false; });
    document.addEventListener('paste', function(e) { e.preventDefault(); return false; });
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            var k = e.key.toLowerCase();
            if (['c', 'a', 'x', 'v', 'p', 's', 'u'].includes(k)) {
                e.preventDefault();
                return false;
            }
        }
        // F12 / Inspect Elements block
        if(e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'i')) {
            e.preventDefault();
            return false;
        }
    });
})();
</script>
"""

if "/* CSS Anti-Copy & Anti-Drag */" not in html:
    html = html.replace('</head>', security_tags + '\n</head>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
    
print("Security and Anti-copy system applied to index.html!")
