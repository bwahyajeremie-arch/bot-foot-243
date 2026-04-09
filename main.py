import telebot
from telebot import types

# TON TOKEN ICI
API_TOKEN = '7791940219:AAGP3h1nJJGynF1rikZEXrkLDKzfzcwdc0I'
bot = telebot.TeleBot(API_TOKEN)

users_data = {}

def get_user_data(user_id):
    if user_id not in users_data:
        users_data[user_id] = {'points': 10000, 'referrals': 0}
    return users_data[user_id]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = get_user_data(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('⚽ Parier (Virtuel)')
    btn2 = types.KeyboardButton('💰 Mon Solde')
    btn3 = types.KeyboardButton('🎓 Académie')
    btn4 = types.KeyboardButton('📲 Mode Data Éco')
    btn5 = types.KeyboardButton('📞 Contact Agent')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, f"Salut champion ! 🎁 Cadeau : {user['points']} points offerts !", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '💰 Mon Solde')
def show_balance(message):
    user = get_user_data(message.from_user.id)
    bot.reply_to(message, f"💵 Solde : {user['points']} points.")

@bot.message_handler(func=lambda message: message.text == '🎓 Académie')
def formation(message):
    bot.send_message(message.chat.id, "Apprends à parier avec le code AFRO243 !")

bot.polling()
