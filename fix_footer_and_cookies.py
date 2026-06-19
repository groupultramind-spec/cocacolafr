import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace AB InBev with Coca Cola in copyright
html = html.replace("AB InBev", "Coca Cola")
html = html.replace("© Ambev", "© Coca Cola")

# Remove old Cookie Settings label
html = html.replace('"label":"Cookie Settings"', '"label":""')
html = html.replace('Cookie Settings', '')

# Remove "Jurídico" if it's there alone
html = html.replace('"title":"Jurídico"', '"title":""')

new_cookie_banner = """
<style>
/* Block old cookie banners */
#onetrust-consent-sdk, .ot-sdk-container, #onetrust-banner-sdk {
    display: none !important;
}

/* Custom Coca-Cola Cookie Banner */
.custom-cookie-banner {
    position: fixed;
    bottom: 20px;
    left: 20px;
    right: 20px;
    background-color: #ffffff;
    border-top: 5px solid #e31837;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    padding: 20px 30px;
    z-index: 2147483647; /* Max z-index */
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 12px;
    font-family: 'Barlow', 'Inter', sans-serif;
    gap: 20px;
}
.custom-cookie-text {
    font-size: 14px;
    color: #444;
    line-height: 1.5;
}
.custom-cookie-text strong {
    color: #e31837;
    font-size: 18px;
    display: block;
    margin-bottom: 5px;
    font-weight: 800;
}
.custom-cookie-btn {
    background-color: #e31837;
    color: #ffffff;
    border: none;
    padding: 14px 28px;
    font-weight: bold;
    font-size: 15px;
    border-radius: 30px;
    cursor: pointer;
    white-space: nowrap;
    transition: 0.3s;
    box-shadow: 0 4px 10px rgba(227, 24, 55, 0.3);
}
.custom-cookie-btn:hover {
    background-color: #b5132c;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(227, 24, 55, 0.4);
}
@media (max-width: 768px) {
    .custom-cookie-banner {
        flex-direction: column;
        text-align: center;
        bottom: 0;
        left: 0;
        right: 0;
        border-radius: 20px 20px 0 0;
        padding: 20px;
    }
    .custom-cookie-btn {
        width: 100%;
        margin-top: 10px;
    }
}
</style>
<div class="custom-cookie-banner" id="customCookieBanner">
    <div class="custom-cookie-text">
        <strong>🍪 Sua Privacidade é Nossa Prioridade</strong>
        Utilizamos cookies para personalizar sua experiência, melhorar o desempenho do site e entregar conteúdos no padrão de qualidade Coca-Cola. Ao continuar navegando, você concorda com a nossa política de privacidade.
    </div>
    <button class="custom-cookie-btn" onclick="document.getElementById('customCookieBanner').style.display='none'">Aceitar e Fechar</button>
</div>
"""

if 'id="customCookieBanner"' not in html:
    html = html.replace('</body>', new_cookie_banner + '\n</body>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Footer updated and custom cookie banner added!")
