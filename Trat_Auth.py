import telebot
import subprocess

bot = telebot.TeleBot('<TOKEN>')

AUTHORIZED_CHAT_IDS = ['<CHAT ID 1>', '<CHAT ID 2>']  # Replace with your authorized chat IDs


@bot.message_handler(func=lambda message: True)
def execute_command(message):
    if str(message.chat.id) not in AUTHORIZED_CHAT_IDS:
        bot.reply_to(message, "You are not authorized to use this bot.")
        return

    command = message.text
    if not command:
        bot.reply_to(message, "Please enter a command.")
        return

    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()
        if not output:
            output = result.stderr.decode()
        if not output:  # Check if output is still empty
            output = "Command executed successfully."
    except subprocess.CalledProcessError as e:
        output = str(e)
    bot.reply_to(message, output)

bot.polling()
