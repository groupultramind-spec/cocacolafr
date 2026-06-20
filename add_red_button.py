import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

script = """
<script>
// Prevent React from deleting our custom button
setInterval(function() {
    var pElements = Array.from(document.querySelectorAll("p"));
    var targetP = pElements.find(p => p.textContent.includes("Tudo em um só lugar"));
    if (targetP && !document.getElementById("custom_atendimento_btn")) {
        var btnContainer = document.createElement("div");
        btnContainer.className = "is-padding-left-xl is-margin-top-m";
        btnContainer.id = "custom_atendimento_btn";
        btnContainer.innerHTML = '<br><a href="https://wa.me/5511933684266" style="display: inline-block; background-color: #e31837; color: #ffffff; padding: 12px 24px; border-radius: 24px; font-family: \\\'Barlow\\\', sans-serif; font-weight: bold; font-size: 16px; text-decoration: none; transition: 0.3s; margin-top: 15px; margin-bottom: 25px;">Falar com um Atendente</a>';
        
        // Insert right below the paragraph
        targetP.insertAdjacentElement("afterend", btnContainer);
    }
}, 500);
</script>
</body>
"""

# Avoid multiple injections
if 'id="custom_atendimento_btn"' not in html:
    html = html.replace('</body>', script)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Red button injected!")
