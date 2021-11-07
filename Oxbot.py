import telebot
from config import *
from keyboards import *
from my_wallet import *

import os
from flask import Flask, request
server = Flask(__name__) #Flask server object




@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    msg_type = message.chat.type
    username = message.from_user.username
    userID = message.from_user.id
    
    if msg_type == "private":
        OxDB.add_user(userID)
        
        user_exists = OxDB.user_exists(userID)
        
        """
        if user_exists == True:
            msg = "Welcome Back {} use the menu button to get started".format(message.from_user.username)
        else:
            msg = "Welcome {} use the menu button to get started".format(message.from_user.username)
        """
        
        bot.send_message(chat_id,welcome_text,reply_markup=home_key())
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    else:
        pass


@bot.message_handler(content_types=['text'])
def send_command(message):
    TASK = None
    chat_id = message.chat.id
    msg_type = message.chat.type
    userID = message.from_user.id
    
    if msg_type == "private":

        if message.text == "Home":
            bot.send_message(chat_id,"🏠",reply_markup=home_key())
            bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        
        elif message.text == "Create New wallet":
            msg = "Please enter wallet name"
            msgs = bot.reply_to(message,msg)
            bot.register_next_step_handler(msgs,create_wallet)
    
        elif message.text == "View Wallet":
            bot.send_message(chat_id,"Here are your wallets",reply_markup = show_wallets(userID)) #the users id is passed here to get the users wallet list
        
        elif message.text == "Add existing wallet":
            msgs = bot.send_message(chat_id,"Enter wallet name",reply_markup = confirm_btn())
            bot.register_next_step_handler(msgs, add_new_wallet)
        
        
        elif message.text == "Recieve":
            address = OxDB.current_wallet(userID) # Get the current wallet from database
            
            bot.send_message(chat_id,f"Send your coin to this address {address}")
        
        elif message.text == "Send":
            msgs = bot.send_message(chat_id,"Enter reciever's address")
            bot.register_next_step_handler(msgs,get_reciever_address)
        
        elif message.text == "❓ Help":
            bot.send_message(chat_id,help_text)
        
        elif message.text == admin_key:
             bot.send_message(chat_id,help_text)
    else:
        pass
        



# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()


#bot.infinity_polling()


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://pacific-oasis-28054.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))




