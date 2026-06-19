#!/bin/bash

echo "Instalando dependências..."
pip3 install -r requirements.txt

echo "Iniciando o Site (app.py) em background..."
nohup python3 app.py > site.log 2>&1 &

echo "Iniciando o Bot (bot_admin.py) em background..."
nohup python3 bot_admin.py > bot.log 2>&1 &

echo "Tudo pronto! Site e Bot estão rodando."
