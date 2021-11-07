from config import *
from telebot.types import *
from OxWalletDB import OxWallet_DB
from Algo import (show_account_in_explorer,show_transaction_in_explorer,
    recent_algo_transactions)

OxDB = OxWallet_DB()

import base64 

#show_account_in_explorer(wallet_address)
#show_account_in_explorer(asset_id)
#show_transaction_in_explorer(txn)
#recent_algo_transactions(wallet_address)


def home_key():
    keyboard = ReplyKeyboardMarkup(True)
    keyboard.row("Create New wallet","View Wallet")
    keyboard.row("Add existing wallet","❓ Help")
    return(keyboard)

def Backup_wallet():
    keyboard = ReplyKeyboardMarkup(True)
    keyboard.row(KeyboardButton("Backup Wallet phrase"))
    return(keyboard)

def show_wallets(user_id):
    """ This is for showing the wallets a user has or created """
    
    wallets = OxDB.show_wallets(user_id)
    keyboard = InlineKeyboardMarkup()
    for wallet in wallets:
        callback_data =  str("0xWA-"+wallet['address'])
        keyboard.add(InlineKeyboardButton(wallet["name"],callback_data=callback_data))
    return(keyboard)

def wallet_btn(coins):
    """ This is for displaying the contents of a particular wallet """
    keyboard = InlineKeyboardMarkup()
        
    callback_data= f"0xAL-{coins['address']}"
    coin_name = f"Algo ({coins['algo_amount']})"

    keyboard.add(InlineKeyboardButton("View Account in Xplorer", url=show_account_in_explorer(coins['address'])))


    keyboard.add(InlineKeyboardButton(coin_name, callback_data=callback_data))
    coins = coins['assets']
        
    for coin in coins:
        callback_data= f"0xCA-{coin['id']}"
        coin_name = f"{coin['unit']} ({coin['amount']})"
        keyboard.add(InlineKeyboardButton(coin_name, callback_data=callback_data))

    return(keyboard)


def view_txn_btn(txn):
    keyboard = InlineKeyboardMarkup()
    text = "View transaction progress"
    keyboard.add(InlineKeyboardButton(text,url=txn["link"]))
    
    return(keyboard)

def txn_btns():
    keyboard = ReplyKeyboardMarkup(True)
    keyboard.row("Send","Recieve")
    keyboard.row(KeyboardButton("Home"))
    return(keyboard)

def confirm_btn():
    keyboard = ReplyKeyboardMarkup(True)
    keyboard.row(KeyboardButton("Confirm"))
    keyboard.row(KeyboardButton("Home"))
    return(keyboard)
