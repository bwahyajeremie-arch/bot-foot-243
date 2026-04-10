import logging
import random
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================= CONFIGURATION =================
# Ton Token Telegram officiel
TOKEN = "7791940219:AAGP3h1nJJGynF1rikZEXrkLDKzfzcwdc0I"
# Remplace les X par ton vrai numéro de téléphone (ex: 243810000000)
WHATSAPP_NUMBER = "https://wa.me/243XXXXXXXXX" 

# ================= BASE DE DONNÉES =================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    balance INTEGER DEFAULT 10000,
    referrals INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bets (
    user_id TEXT,
    amount INTEGER,
    result TEXT
)
""")
conn.commit()

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

# ================= INITIALISATION UTILISATEUR =================
def init_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (user_id, balance, referrals) VALUES (?, ?, ?)",
            (user_id, 10000, 0),
        )
        conn.commit()

# ================= COMMANDE /START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    init_user(user_id)

    # Gestion du parrainage
    if context.args:
        ref = context.args[0]
        if ref != user_id:
            init_user(ref)
            cursor.execute("UPDATE users SET balance = balance + 2000 WHERE user_id=?", (ref,))
            conn.commit()

    keyboard = [
        [InlineKeyboardButton("💰 Contacter Agent (Dépôts/Retraits)", url=WHATSAPP_NUMBER)],
        [InlineKeyboardButton("🎓 Formation Académie", callback_data="formation")],
    ]

    await update.message.reply_text(
        "⚽ *Bienvenue sur Expert Foot 243*\n\n"
        "🎁 Cadeau de bienvenue : *10 000 points* virtuels offerts !\n\n"
        "Utilise `/parier montant equipe` pour jouer.\n"
        "Utilise `/direct` pour les scores en mode Éco.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ================= COMMANDE /SOLDE =================
async def solde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    init_user(user_id)
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cursor.fetchone()[0]
    await update.message.reply_text(f"💰 Ton solde : {balance} points virtuels.")

# ================= COMMANDE /PARIER =================
async def parier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    init_user(user_id)

    if len(context.args) < 1:
        await update.message.reply_text("❌ Usage: `/parier montant` (ex: /parier 500)", parse_mode="Markdown")
        return

    try:
        montant = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Erreur : Le montant doit être un chiffre.")
        return

    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cursor.fetchone()[0]

    if montant <= 0:
        await update.message.reply_text("❌ Mise invalide.")
        return
    if montant > balance:
        await update.message.reply_text(f"❌ Solde insuffisant (Max: {balance})")
        return

    result = random.choice(["win", "lose"])

    if result == "win":
        gain = montant * 2
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (montant, user_id))
        msg = f"🎉 GAGNÉ ! Ton équipe a triomphé. Tu gagnes {gain} points."
    else:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (montant, user_id))
        msg = f"😢 PERDU ! Ton équipe a échoué. Tu perds {montant} points."

    cursor.execute("INSERT INTO bets VALUES (?, ?, ?)", (user_id, montant, result))
    conn.commit()
    await update.message.reply_text(msg)

# ================= COMMANDE /DIRECT (MODE ÉCO) =================
async def direct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
⚽ *LIVE FOOT (MODE ÉCO - DATA SAVER)*

🇨🇩 Léopards 1 - 0 Jamaique
🇪🇸 Real Madrid 2 - 1 Barça
🏴 Arsenal 0 - 0 Chelsea

📡 *Infos :* Inscription bonus avec code **AFRO243**
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# ================= ACADÉMIE & FORMATION =================
async def formation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 C'est quoi une Cote ?", callback_data="cote")],
        [InlineKeyboardButton("💸 Gestion du Budget", callback_data="budget")],
        [InlineKeyboardButton("🔥 Inscription Bonus", callback_data="bet")],
    ]
    await update.message.reply_text(
        "🎓 *Académie des Gagnants Expert Foot 243*\n\nChoisis une leçon :",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cote":
        text = "📊 *La Cote :* C'est le multiplicateur de ton gain. Si tu mises 1000 sur une cote de 2.00, tu gagnes 2000."
    elif query.data == "budget":
        text = "💸 *Budget :* Ne mise jamais plus de 10% de ton capital sur un seul match pour durer dans le jeu."
    elif query.data == "bet":
        text = "🔥 *Inscription :* Crée ton compte sur AfroPari avec le code promo **AFRO243** pour recevoir +300% de bonus."

    await query.edit_message_text(text, parse_mode="Markdown")

# ================= LANCEMENT =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("solde", solde))
    app.add_handler(CommandHandler("parier", parier))
    app.add_handler(CommandHandler("direct", direct))
    app.add_handler(CommandHandler("formation", formation))
    app.add_handler(CallbackQueryHandler(callback))

    print("🚀 Bot Expert Foot 243 en ligne...")
    app.run_polling()

if __name__ == "__main__":
    main()
