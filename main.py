import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import google.generativeai as genai

# ================= CONFIGURATION =================
TOKEN = "8795049125:AAFP1WGFen_7m4wtu_CemPrza3EwgdgrGFg"
ADMIN_ID = 8365482737
ADMIN_PASSWORD = "je00remie00"
GEMINI_KEY = "AIzaSyBD8TdeGke_pgDb8tqsYtj3f7Kjiuq98tA"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TOKEN)

# ================= BASE DE DONNÉES =================
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0)")
conn.commit()

# ================= FONCTIONS IA EXPERT =================
def ia_expert(message_text, mode="general"):
    if mode == "analyse":
        prompt = f"Analyse ce match de football pour un parieur : {message_text}. Donne les chances de victoire, l'état de forme et un pronostic (ex: Plus de 2.5 buts). Sois précis."
    else:
        prompt = f"Tu es l'expert de Kivu Super App 243. Réponds à cette question sur le foot ou les paris : {message_text}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Désolé, l'expert est en train d'analyser les matchs. Réessaie !"

# ================= COMMANDES =================
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup(row_width=2)
    btn_analyse = InlineKeyboardButton("⚽ Analyser un Match", callback_data="btn_analyse")
    btn_formation = InlineKeyboardButton("📚 Formation Parieur", callback_data="btn_formation")
    btn_points = InlineKeyboardButton("💰 Mes Points", callback_data="btn_points")
    markup.add(btn_analyse, btn_formation, btn_points)
    
    bot.send_message(message.chat.id, "🌟 **KIVU SUPER APP 243 - EXPERT** 🌟\n\nBienvenue ! Je suis ton assistant IA. Je peux analyser tes matchs et t'apprendre à parier.", reply_markup=markup, parse_mode="Markdown")

# ================= GESTION DES CLICS (CALLBACKS) =================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "btn_analyse":
        bot.send_message(call.message.chat.id, "📝 Écris-moi le nom du match (ex: Real Madrid vs Barcelone) et je vais l'analyser pour toi !")
    
    elif call.data == "btn_formation":
        text_formation = (
            "🎓 **FORMATION COMPLÈTE DU PARIEUR**\n\n"
            "1️⃣ **C'est quoi une cote ?** Plus la cote est petite, plus la chance de gagner est grande.\n"
            "2️⃣ **Gestion d'argent :** Ne parie jamais tout ton capital d'un coup !\n"
            "3️⃣ **Les types de paris :** 1X2, Double chance, Over/Under.\n\n"
            "Pose-moi une question spécifique si tu veux en savoir plus !"
        )
        bot.send_message(call.message.chat.id, text_formation, parse_mode="Markdown")
        
    elif call.data == "btn_points":
        cursor.execute("SELECT points FROM users WHERE id=?", (call.from_user.id,))
        res = cursor.fetchone()
        p = res[0] if res else 0
        bot.send_message(call.message.chat.id, f"💰 Tu as actuellement **{p} points**.")

# ================= GESTION DES MESSAGES TEXTE =================
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    # L'IA répond à tout ce que l'utilisateur écrit
    reponse = ia_expert(message.text)
    bot.reply_to(message, reponse)

bot.infinity_polling()
