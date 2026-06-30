import json
import os
import requests
import re
import time

def check_status():
    print('\n=============================================')
    print('          DIAGNÓSTICO DO SISTEMA             ')
    print('=============================================')
    
    # 1. Checar Número do WhatsApp
    db_file = 'database.json'
    numero = 'Não definido'
    if os.path.exists(db_file):
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
                numero = db.get('whatsapp_number', 'Não definido')
        except:
            pass
    print(f'[+] Número WhatsApp Atual: +{numero}')
    
    # 2. Ping no Google
    try:
        start = time.time()
        requests.get('https://www.google.com', timeout=3)
        ping = int((time.time() - start) * 1000)
        print(f'[+] Conexão com Google: OK ({ping}ms) - Rodando liso!')
    except:
        print('[-] Conexão com Google: FALHA (Verifique a internet)')
        
    # 3. Checar Tags do Google
    tag_ok = False
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
            if 'googletagmanager.com/gtag/js' in html and 'AW-18242962464' in html:
                tag_ok = True
    except:
        pass
    print(f'[+] Tag Google (Site Principal): {"VÁLIDA e ATIVA" if tag_ok else "NÃO ENCONTRADA"}')
    
    tag_app_ok = False
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_code = f.read()
            if 'AW-18242962464' in app_code and 'conversion' in app_code:
                tag_app_ok = True
    except:
        pass
    print(f'[+] Tag Google (Conversão Zap): {"VÁLIDA e ATIVA" if tag_app_ok else "NÃO ENCONTRADA"}')

    print('=============================================\n')

if __name__ == "__main__":
    check_status()
