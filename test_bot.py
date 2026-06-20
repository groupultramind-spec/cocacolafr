import os, sys, json
sys.path.insert(0, r'd:\CocaCola')
from app import get_secrets
import requests

with open('test_bot_log.txt', 'w') as log:
    secrets = get_secrets()
    log.write(f'Secrets: {secrets}\n')
    if secrets:
        token = secrets['token']
        channel_id = secrets['channel_id']
        url = f'https://api.telegram.org/bot{token}/getMe'
        try:
            r = requests.get(url, timeout=5)
            log.write(f'getMe response: {r.json()}\n')
            
            test_msg_url = f'https://api.telegram.org/bot{token}/sendMessage'
            r2 = requests.post(test_msg_url, json={'chat_id': channel_id, 'text': 'Test from script'}, timeout=5)
            log.write(f'sendMessage response: {r2.json()}\n')
        except Exception as e:
            log.write(f'Error: {e}\n')
