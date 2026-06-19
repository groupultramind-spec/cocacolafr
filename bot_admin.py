import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from cryptography.fernet import Fernet
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'database.json')

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    try:
        with open(os.path.join(BASE_DIR, 'secret.key'), 'rb') as f:
            key = f.read()
        fernet = Fernet(key)
        with open(os.path.join(BASE_DIR, 'secrets.enc'), 'rb') as f:
            enc_data = f.read()
        secrets = json.loads(fernet.decrypt(enc_data).decode('utf-8'))
        TOKEN = secrets.get('token')
    except Exception as e:
        print("ERRO ao descriptografar token:", e)
        exit(1)

bot = telebot.TeleBot(TOKEN)

# States
user_states = {}
STATE_AWAITING_NUMBER = 1

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"whatsapp_number": "", "logs": []}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    btn_relatorio = InlineKeyboardButton("📊 Ver Relatório de Acessos", callback_data="btn_relatorio")
    btn_mudar_numero = InlineKeyboardButton("⚙️ Mudar Número WhatsApp", callback_data="btn_mudar_numero")
    markup.add(btn_relatorio, btn_mudar_numero)
    return markup

@bot.message_handler(commands=['start', 'admin'])
def send_welcome(message):
    bot.reply_to(message, "👋 Olá, Admin! Eu sou o Bot de Gestão do Site.\nEscolha uma opção no menu abaixo:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "btn_relatorio":
        db = load_db()
        logs = db.get("logs", [])
        entradas = sum(1 for log in logs if log['event'] == 'ENTRADA')
        saidas = sum(1 for log in logs if log['event'] == 'SAIDA_WHATSAPP')
        
        saidas_list = [log for log in logs if log['event'] == 'SAIDA_WHATSAPP']
        ultimas_saidas = saidas_list[-5:]
        
        texto_ultimos = ""
        for i, log in enumerate(reversed(ultimas_saidas), 1):
            action = str(log.get('action', 'Contato Geral')).upper()
            texto_ultimos += f"*{i}. Redirecionado p/ WhatsApp* ( {log['timestamp']} )\n📱 {log['device']} | 🌍 {log['state']}, {log['country']}\n⚙️ *Intenção:* {action}\n\n"
            
        if not texto_ultimos:
            texto_ultimos = "Nenhum redirecionamento registrado ainda.\n"
            
        taxa = f"{(saidas/entradas)*100:.1f}%" if entradas > 0 else "0%"
        texto_relatorio = (
            "📊 *Relatório Oficial de Conversões*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 *Visitantes Totais no Site:* `{entradas}`\n"
            f"🚀 *Leads Redirecionados:* `{saidas}`\n"
            f"📈 *Taxa de Conversão:* `{taxa}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 *Últimos Leads (WhatsApp):*\n\n"
            f"{texto_ultimos}"
        )
        
        markup = InlineKeyboardMarkup()
        btn_voltar = InlineKeyboardButton("🔙 Voltar ao Menu Inicial", callback_data="btn_voltar")
        markup.add(btn_voltar)
        
        bot.edit_message_text(texto_relatorio, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
        
    elif call.data == "btn_voltar":
        user_states[chat_id] = None
        bot.edit_message_text("👋 Olá, Admin! Eu sou o Bot de Gestão do Site.\nEscolha uma opção no menu abaixo:", chat_id, call.message.message_id, reply_markup=main_menu())
        
    elif call.data == "btn_mudar_numero":
        db = load_db()
        numero_atual = db.get('whatsapp_number', 'Não definido')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Voltar", callback_data="btn_voltar"))
        
        bot.edit_message_text(
            f"✏️ Por favor, digite o novo número do WhatsApp no chat.\n*(Apenas números, com DDI e DDD. Ex: 5511999999999)*\n\n📱 *Número atual:* `{numero_atual}`", 
            chat_id, 
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
        user_states[chat_id] = STATE_AWAITING_NUMBER
        
    elif call.data.startswith("confirm_num_"):
        novo_numero = call.data.split("confirm_num_")[1]
        db = load_db()
        db["whatsapp_number"] = novo_numero
        save_db(db)
        user_states[chat_id] = None
        bot.edit_message_text(f"✅ Número alterado com sucesso para: `{novo_numero}`", chat_id, call.message.message_id, parse_mode="Markdown")
        bot.send_message(chat_id, "Menu Principal:", reply_markup=main_menu())
        
    elif call.data == "cancelar":
        user_states[chat_id] = None
        bot.edit_message_text("❌ Ação cancelada.", chat_id, call.message.message_id)
        bot.send_message(chat_id, "Menu Principal:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    if user_states.get(chat_id) == STATE_AWAITING_NUMBER:
        numero = message.text.strip()
        
        if not re.match(r'^\d{10,15}$', numero):
            bot.reply_to(message, "⚠️ Erro: O número deve conter apenas dígitos e ter entre 10 e 15 caracteres. Tente enviar novamente.")
            return
            
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("✅ Confirmar Alteração", callback_data=f"confirm_num_{numero}"))
        markup.row(InlineKeyboardButton("❌ Cancelar", callback_data="cancelar"))
        
        bot.reply_to(message, f"Você digitou o número: `{numero}`.\nDeseja salvar essa configuração para o site?", reply_markup=markup, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Use os botões para interagir com o sistema.", reply_markup=main_menu())

if __name__ == "__main__":
    print("Iniciando Bot...")
    bot.infinity_polling()
