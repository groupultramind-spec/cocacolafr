import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_cookie_banner = """
<style>
/* Block old cookie banners */
#onetrust-consent-sdk, .ot-sdk-container, #onetrust-banner-sdk {
    display: none !important;
}

/* Custom Coca-Cola Cookie Banner (Black/Yellow) */
.custom-cookie-banner {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #000000;
    padding: 20px 40px;
    z-index: 2147483647; /* Max z-index */
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'Barlow', 'Inter', sans-serif;
    gap: 30px;
    box-shadow: 0 -4px 10px rgba(0,0,0,0.3);
}
.custom-cookie-text-container {
    flex: 1;
}
.custom-cookie-title {
    color: #ffffff;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 8px;
}
.custom-cookie-text {
    font-size: 13px;
    color: #cccccc;
    line-height: 1.5;
}
.custom-cookie-text a {
    color: #ffeb00;
    text-decoration: underline;
    font-weight: bold;
}
.custom-cookie-buttons {
    display: flex;
    gap: 15px;
}
.custom-cookie-btn {
    background-color: #ffeb00;
    color: #000000;
    border: none;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 14px;
    cursor: pointer;
    white-space: nowrap;
    transition: 0.3s;
    border-radius: 4px;
}
.custom-cookie-btn:hover {
    background-color: #e6d400;
}
.custom-cookie-close {
    color: #999;
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    padding: 0 0 0 10px;
}
.custom-cookie-close:hover {
    color: #fff;
}

@media (max-width: 900px) {
    .custom-cookie-banner {
        flex-direction: column;
        padding: 20px;
        gap: 15px;
    }
    .custom-cookie-buttons {
        width: 100%;
        flex-direction: column;
        gap: 10px;
    }
    .custom-cookie-btn {
        width: 100%;
    }
    .custom-cookie-close {
        position: absolute;
        top: 15px;
        right: 15px;
    }
}
</style>
<div class="custom-cookie-banner" id="customCookieBanner">
    <div class="custom-cookie-text-container">
        <div class="custom-cookie-title">Utilizamos cookies para melhorar sua experiência</div>
        <div class="custom-cookie-text">
            Ao clicar em "Aceitar todos os cookies", você concorda com o armazenamento de cookies no seu dispositivo para melhorar a navegação no site, analisar a utilização do site e ajudar nas nossas iniciativas de marketing. Conheça a <a href="#">Política de Privacidade</a>
        </div>
    </div>
    <div class="custom-cookie-buttons">
        <button class="custom-cookie-btn" onclick="document.getElementById('customCookieBanner').style.display='none'">Rejeitar todos</button>
        <button class="custom-cookie-btn" onclick="document.getElementById('customCookieBanner').style.display='none'">Aceitar todos os cookies</button>
    </div>
    <button class="custom-cookie-close" onclick="document.getElementById('customCookieBanner').style.display='none'">✕</button>
</div>
"""

# Replace the previous custom banner injection logic
if '<div class="custom-cookie-banner" id="customCookieBanner">' in html:
    # Use regex to find and replace the entire previous banner style and div
    html = re.sub(r'<style>\s*/\* Block old cookie banners \*/.*?</style>\s*<div class="custom-cookie-banner" id="customCookieBanner">.*?</div>', new_cookie_banner.strip(), html, flags=re.DOTALL)
else:
    html = html.replace('</body>', new_cookie_banner + '\n</body>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Cookie banner updated to Black & Yellow design!")
