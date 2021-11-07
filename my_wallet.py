import telebot
from config import *
from keyboards import *
from telebot.types import *
from OxWalletDB import OxWallet_DB
from Algo import (generate_algorand_account,wallet_holdings,
	show_wallet_address,show_private_key,send_algo,recent_algo_transactions)



OxDB = OxWallet_DB()
bot = telebot.TeleBot(TOKEN)

            
        

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    userID = call.message.chat.id
    try:
        if call.data.startswith("0xWA"):
            """ Here we get the wallet's content using the wallet address """
            
            address = call.data.split("0xWA-")[1]
            set_current = OxDB.set_current_wallet(userID, address) #sets the current wallet a user is interacting with
            my_address = OxDB.current_wallet(userID)[0] # Get the current wallet from database
            my_wallet = wallet_holdings(address)
            
            try:
                msg = my_wallet["message"]
                msg = f"""
                \n Send algo to this wallet to begin using wallet\n
                \n{address}"""
                
                bot.send_message(chat_id=call.message.chat.id,text=msg,reply_markup = home_key())
            except KeyError:
                
                bot.edit_message_text(chat_id=call.message.chat.id,
                	text="Select Coin u want to send or receive", message_id=call.message.message_id,
                	reply_markup=wallet_btn(my_wallet), parse_mode='HTML')


        elif call.data.startswith("0xCA"):
            """ Here we open up send and recieve button for the coin """

            asset_id = int(call.data.split("0xCA-")[1])
            address = OxDB.current_wallet(userID)[0] # Get the current wallet from database

            algo_info = wallet_holdings(address)
            try:
                msg = algo_info["message"]
            except KeyError:
                coins = algo_info['assets']
                asset = [coin for coin in coins if int(coin["id"]) == asset_id][0]
                
                OxDB.create_txn(userID,asset['name'],float(asset['amount'])) # Save transaction to database
                
                msg = f"""Coin Name: {asset['name']}
                Coin symbol: {asset['unit']}
                Amount Available:{asset['amount']}
                Asset ID: {asset['id']}
                Address:{address}"""

                print(msg)
                
            bot.send_message(chat_id=call.message.chat.id,text=msg,reply_markup = home_key())
        
        elif call.data.startswith("0xAL"):
            address = call.data.split("0xAL-")[1]
            
            algo_info = wallet_holdings(address)
            try:
                msg = algo_info["message"]
            except KeyError:
                OxDB.create_txn(userID,"Algorand",float(algo_info['algo_amount'])) # Save transaction to database
                       
                msg = f"""You can send or receive Algorand
                Coin symbol: Algo
                Amount Available: {algo_info['algo_amount']}
                Address:{address}"""

                print(recent_algo_transactions(address),"djvdvjeueiodfjhn")
                
            bot.send_message(chat_id=call.message.chat.id,text=msg,reply_markup = txn_btns())

        
        else:
            pass
    except Exception as e:
        print(f"CALLBACK ERROR : {e}")
        pass



# CREATING NEW WALLETS


def create_wallet(message):
    chat_id = message.chat.id
    userID = message.from_user.id
    
    if message.text != "":
        wallet_name = message.text
        my_wallet = generate_algorand_account(wallet_name)
        
        
        #Here we create the user wallet
        
        OxDB.add_user_wallet(userID,wallet_name,my_wallet["address"],my_wallet["phrase"],my_wallet["key"])
        
        msg = bot.send_message(chat_id,"Wallet created successfully",reply_markup=Backup_wallet())
        bot.register_next_step_handler(msg,backup_wallet)
    else:
        bot.send_message(chat_id,"oops unrecognized command",reply_markup=home_key())


def add_new_wallet(message):
    chat_id = message.chat.id
    userID = message.from_user.id
    
    wallet_name = message.text
    OxDB.add_user_wallet(userID,wallet_name,"0xWA",None,None)
    msg = bot.send_message(chat_id,"Add wallet phrase",reply_markup=confirm_btn())
    bot.register_next_step_handler(msg,add_wallet_by_phrase)
    

def add_wallet_by_phrase(message):
    chat_id = message.chat.id
    userID = message.from_user.id
    
    
    #update the most recent wallet_address
    passphrase = message.text
    try:
        private_key = show_private_key(passphrase)
        wallet_address = show_wallet_address(passphrase)
        
        OxDB.add_wallet_address(userID,wallet_address, private_key)
        bot.send_message(chat_id,"Wallet is now added",reply_markup=home_key())
    except Exception as e:
        print(f"PASSPHRASE ERROR : {e}")
        msg = bot.send_message(chat_id,"Add a valid wallet phrase",reply_markup=confirm_btn())
        #bot.register_next_step_handler(msg,add_wallet_by_phrase)
    
def backup_wallet(message):
    chat_id = message.chat.id
    userID = message.from_user.id
    
    recent_wallet = OxDB.most_recent_wallet(userID)
    passphrase = recent_wallet[3]
        	
    msg = f"""
    Here is your passphrase keep it safe as we do not save them.\n
    Copy it as you cannot go back.
    """
    bot.send_message(chat_id,msg,reply_markup=confirm_btn())
    
    msgs = bot.send_message(chat_id,f"{passphrase}")
    
    bot.register_next_step_handler(msgs,backup_phrase)


def backup_phrase(message):
    chat_id = message.chat.id
    msgs = bot.send_message(chat_id,"please enter your wallet phrase",reply_markup=confirm_btn())
    bot.register_next_step_handler(msgs,confirm_backup)


def confirm_backup(message):
    chat_id = message.chat.id
    userID = message.from_user.id
    
    recent_wallet = OxDB.most_recent_wallet(userID)
    passphrase = recent_wallet[3]
    wallet_address = recent_wallet[2]
        	
    if message.text == passphrase:
        OxDB.remove_passphrase(wallet_address)
        bot.send_message(chat_id,"Wallet backed-up successfully",reply_markup=home_key())
    else:
        msgs = bot.send_message(chat_id,"Incorrect please try again or create new wallet",reply_markup=confirm_btn())
        bot.register_next_step_handler(msgs,backup_phrase)



# THIS IS FOR TRANSACTIONS


def initialize_txn(message):
    chat_id = message.chat.id
    msgs = bot.send_message(chat_id,"Here are your wallets",reply_markup = show_wallets())


def get_reciever_address(message):
    chat_id = message.chat.id
    userID = message.from_user.id
    
    recent_txn = OxDB.return_recent_txn(userID)
    txn_id = recent_txn[0]
    reciever_address = message.text
    OxDB.add_receiver_address(txn_id,reciever_address)
    
    msg = bot.send_message(chat_id,"Enter amount to send")
    bot.register_next_step_handler(msg, confirm_transaction)
        

def confirm_transaction(message):
    chat_id = message.chat.id
    userID = message.from_user.id
    
    try:
        amount = float(message.text)
        
        recent_txn = OxDB.return_recent_txn(userID)
        txn_id = recent_txn[0]
        OxDB.add_amount_to_send(txn_id,amount)
        
    except:
        msg = bot.send_message(chat_id,"Welcome back", reply_markup =home_key())
        #bot.register_next_step_handler(msg, confirm_transaction)
    
    recent_txn = OxDB.return_recent_txn(userID)
    txn_id = recent_txn[0]
    txn_data = OxDB.return_txn_data(txn_id)
    
    coin_amount = txn_data[4]
    amount_to_send = txn_data[5]
    
    
    if amount_to_send > coin_amount*10000:
        msg = bot.send_message(chat_id,"Insufficient fund!! Enter a valid amount")
        bot.register_next_step_handler(msg, confirm_transaction)
    else:
        msg = f"""here is a summary of your input:\nsend {txn_data[2]} to : {txn_data[3]}\namount: {txn_data[5]}"""
        msgs = bot.send_message(chat_id,msg,reply_markup = confirm_btn())
        bot.register_next_step_handler(msgs,Send_Coin)


def Send_Coin(message):
    chat_id = message.chat.id
    userID = message.from_user.id
    
    recent_txn = OxDB.return_recent_txn(userID)
    txn_id = recent_txn[0]
    txn_data = OxDB.return_txn_data(txn_id)
    
    
    
    coin_name = txn_data[2]
    amount = int(txn_data[5])
    receiver_address = txn_data[3]
    
    sender_address = OxDB.current_wallet(userID)[0] # Get the current wallet from database
    sender_key = OxDB.return_private_key(sender_address)[0]
    
    
    try:
        txn = send_algo(sender_address,receiver_address,amount,sender_key)
        msg = f"""SENDING ({amount}) {coin_name} TO {receiver_address}\n TXNID : {txn['txid']}"""
    except Exception as e:
        msg = f"An error occured because: {e}"

    
    
    msgs = bot.send_message(chat_id,msg,reply_markup=view_txn_btn(txn))
        






