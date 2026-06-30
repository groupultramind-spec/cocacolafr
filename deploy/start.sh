#!/bin/bash

echo "Instalando dependências..."
pip3 install -r requirements.txt

echo "Iniciando o Bot (bot_admin.py) em background..."
nohup python3 bot_admin.py > bot.log 2>&1 &

echo "Verificando Status do Sistema..."
python3 check_status.py

echo "Iniciando o Site (app.py) em foreground..."
python3 app.py
