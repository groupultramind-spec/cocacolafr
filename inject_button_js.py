import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

script = """
<script>
// Prevent React from deleting our custom button
setInterval(function() {
    var benefitsList = document.getElementById("benefits_text");
    if (benefitsList && !document.getElementById("custom_cadastre_btn")) {
        var btnContainer = document.createElement("div");
        btnContainer.className = "is-padding-left-xl is-margin-top-m";
        btnContainer.id = "custom_cadastre_btn";
        btnContainer.innerHTML = '<br><a href="/redirect_whatsapp" style="display: inline-block; background-color: #000000; color: #ffffff; padding: 12px 24px; border-radius: 24px; font-family: \\\'Barlow\\\', sans-serif; font-weight: bold; font-size: 16px; text-decoration: none; transition: 0.3s; margin-top: 15px;">Cadastre-se</a>';
        benefitsList.parentElement.appendChild(btnContainer);
    }
}, 500);
</script>
</body>
"""

# Avoid multiple injections
if 'id="custom_cadastre_btn"' not in html:
    html = html.replace('</body>', script)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
