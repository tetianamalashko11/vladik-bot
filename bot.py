import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

TOKEN = "8930741978:AAFpXGhOpbxb1zcppH32Ji2pxcymFYhDvgI"
bot = telebot.TeleBot(TOKEN)

menu = {
    "kiss": {"name": "😘 Поцелуй", "emoji": "😘"},
    "hug": {"name": "🤗 Объятие", "emoji": "🤗"},
    "borshch": {"name": "🍲 Борщ", "emoji": "🍲"},
    "varenyky": {"name": "🥟 Варенички", "emoji": "🥟"},
    "seledka": {"name": "🐟 Селёдка под шубой", "emoji": "🐟"},
    "pizza": {"name": "🍕 Домашняя пицца", "emoji": "🍕"},
    "tea": {"name": "🍵 Чашечка чая", "emoji": "🍵"},
    "cuddle": {"name": "🛋️ Поваляться вместе", "emoji": "🛋️"},
    "blanket": {"name": "🎬 Пледик и фильм", "emoji": "🎬"},
    "massage": {"name": "💆‍♀️ Массаж", "emoji": "💆‍♀️"},
    "dance": {"name": "💃 Маленький танец от меня", "emoji": "💃"},
    "breakfast": {"name": "🍳 Завтрак в постель", "emoji": "🍳"},
    "talk": {"name": "💬 Просто поговорить", "emoji": "💬"},
    "cat": {"name": "🐱 Картинка с милым котиком", "emoji": "🐱"},
    "photo": {"name": "📸 Фоточка", "emoji": "📸"},
}

carts = {}

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for key, val in menu.items():
        btn = InlineKeyboardButton(f"{val['emoji']} {val['name']}", callback_data=f"add_{key}")
        keyboard.add(btn)
    keyboard.add(InlineKeyboardButton("🛒 Моя корзина", callback_data="view_cart"))
    keyboard.add(InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout"))
    bot.send_message(message.chat.id, "🌸 Меню желаний 🌸\nНажми на любой пункт!", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def add_to_cart(call):
    service_id = call.data[4:]
    user_id = call.from_user.id
    if user_id not in carts:
        carts[user_id] = {}
    carts[user_id][service_id] = carts[user_id].get(service_id, 0) + 1
    bot.answer_callback_query(call.id, f"✅ Добавлено: {menu[service_id]['name']}")

@bot.callback_query_handler(func=lambda call: call.data == "view_cart")
def view_cart(call):
    user_id = call.from_user.id
    cart = carts.get(user_id, {})
    if not cart:
        bot.send_message(call.message.chat.id, "Корзина пуста")
        return
    lines = []
    for sid, qty in cart.items():
        lines.append(f"{menu[sid]['emoji']} {menu[sid]['name']} — {qty} шт.")
    text = "🛒 Твоя корзинка:\n\n" + "\n".join(lines)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu"))
    bot.send_message(call.message.chat.id, text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "checkout")
def checkout(call):
    user_id = call.from_user.id
    cart = carts.get(user_id, {})
    if not cart:
        bot.send_message(call.message.chat.id, "Корзина пуста")
        return
    YOUR_ID = 545035628
    order = f"📦 ЗАКАЗ от {call.from_user.first_name}\n\n"
    for sid, qty in cart.items():
        order += f"{menu[sid]['emoji']} {menu[sid]['name']} — {qty} шт.\n"
    bot.send_message(YOUR_ID, order)
    bot.send_message(call.message.chat.id, "✅ Заказ отправлен! ❤️")
    carts[user_id] = {}

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_to_menu(call):
    start(call.message)

# Запуск бота в отдельном потоке
def run_bot():
    bot.infinity_polling()

# Заглушка для порта (чтобы Render не ругался)
app = Flask(__name__)
@app.route('/')
def home():
    return "Бот работает!"

if __name__ == "__main__":
    print("Бот запущен!")
    # Запускаем бота в фоне
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    # Запускаем веб-сервер на порту 10000
    app.run(host="0.0.0.0", port=10000)
