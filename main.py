import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os
import time

# ================= CONFIGURATION =================
TOKEN = "8795049125:AAFP1WGFen_7m4wtu_CemPrza3EwgdgrGFg" # Ton Token BotFather
ADMIN_ID = 8365482737 # Ton ID récupéré
ADMIN_PASSWORD = "je00remie00" # Ton mot de passe secret

bot = telebot.TeleBot(TOKEN)

# ================= BASE DE DONNÉES =================
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Création de la table avec support affiliation 3 niveaux
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    referrer INTEGER,
    level2 INTEGER,
    level3 INTEGER,
    vip_expire INTEGER DEFAULT 0,
    vip_type TEXT DEFAULT 'none'
)
""")
conn.commit()

# ================= LOGIQUE D'INSCRIPTION =================
def add_user(user_id, referrer=None):
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    if cursor.fetchone():
        return

    l2, l3 = None, None
    if referrer:
        # Chercher le parrain du parrain pour le niveau 2 et 3
        cursor.execute("SELECT referrer, level2 FROM users WHERE id=?", (referrer,))
        data = cursor.fetchone()
        if data:
            l2 = data[0]
            l3 = data[1]

    cursor.execute("INSERT INTO users (id, referrer, level2, level3) VALUES (?, ?, ?, ?)", 
                   (user_id, referrer, l2, l3))
    conn.commit()

    # Distribution des points
    if referrer:
        cursor.execute("UPDATE users SET points = points + 10 WHERE id=?", (referrer,))
    if l2:
        cursor.execute("UPDATE users SET points = points + 5 WHERE id=?", (l2,))
    if l3:
        cursor.execute("UPDATE users SET points = points + 2 WHERE id=?", (l3,))
    conn.commit()

# ================= COMMANDES =================
@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    referrer = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
    add_user(message.from_user.id, referrer)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💰 Gagner des points", callback_data="earn"))
    markup.add(InlineKeyboardButton("🏆 Top Affiliés", callback_data="top_aff"))
    
    bot.send_message(message.chat.id, "👋 Bienvenue sur Kivu Super App 243 !\nUtilise ton lien pour inviter des amis et gagner de l'argent.", reply_markup=markup)

@bot.message_handler(commands=['retirer'])
def retirer(message):
    user_id = message.from_user.id
    cursor.execute("SELECT points FROM users WHERE id=?", (user_id,))
    res = cursor.fetchone()
    points = res[0] if res else 0
    
    if points < 100:
        return bot.send_message(message.chat.id, "❌ Minimum de retrait : 100 points.")
    
    bot.send_message(message.chat.id, f"✅ Demande de retrait envoyée !\nPoints : {points}")
    bot.send_message(ADMIN_ID, f"🚩 ALERTE RETRAIT\nUtilisateur : {user_id}\nPoints : {points}")

# ================= CALLBACKS =================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "earn":
        link = f"https://t.me/{bot.get_me().username}?start={call.from_user.id}"
        bot.send_message(call.message.chat.id, f"🔗 Ton lien de parrainage :\n{link}\n\nPartage-le pour gagner des points !")
    
    elif call.data == "top_aff":
        cursor.execute("SELECT id, points FROM users ORDER BY points DESC LIMIT 10")
        data = cursor.fetchall()
        txt = "🏆 TOP AFFILIÉS :\n\n"
        for u in data:
            txt += f"👤 {u[0]} → {u[1]} pts\n"
        bot.send_message(call.message.chat.id, txt)

print("🤖 Bot en marche...")
bot.infinity_polling()# ================= ADMIN (CORRIGÉ) =================
@bot.message_handler(commands=['admin'])
def admin(message):
    # On vérifie d'abord si c'est bien TOI (le patron)
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "⛔ Accès refusé. Vous n'êtes pas l'administrateur.")

    msg = bot.send_message(message.chat.id, "🔑 Veuillez entrer le mot de passe secret :")
    bot.register_next_step_handler(msg, process_password)

def process_password(message):
    # On compare le texte envoyé avec ton mot de passe configuré
    if message.text == ADMIN_PASSWORD:
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("👥 Utilisateurs", callback_data="users_count"),
            InlineKeyboardButton("📢 Message Groupé", callback_data="broadcast_msg")
        )
        bot.send_message(message.chat.id, "✅ Bienvenue Patron ! Que voulez-vous faire ?", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Mot de passe incorrect. Réessayez avec /admin")

