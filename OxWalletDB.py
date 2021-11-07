import uuid
import sqlite3
from sql_commands import*
from datetime import datetime

class OxWallet_DB(object):
    def __init__(self):
        self.dbname = "OxWallet.db"
        conn = sqlite3.connect(self.dbname)
        sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
        sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.execute(create_table_users)
        cur.execute(create_table_wallets)
        cur.execute(create_table_txn_history)
        conn.close()

    def add_user(self,id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        if self.user_exists(id) == False:
            cur.execute('INSERT INTO UserInfo (user_id,date_joined) VALUES (?,?)',(id, datetime.now(),))
            conn.commit()
            conn.close()
            return("User has been successfully saved ")
        else:
            return("User already exists")
    
    def add_user_wallet(self,user_id, wallet_name,wallet_address,wallet_phrase,private_key):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('INSERT INTO UserWallet (user_id, wallet_name, wallet_address,wallet_phrase,private_key,date_created) VALUES (?,?,?,?,?,?)',(user_id, wallet_name, wallet_address,wallet_phrase,private_key,datetime.now(),))
        conn.commit()
        conn.close()
        return(f"{wallet_name} wallet has been successfully created")
        
    def show_wallets(self,user_id):
        """ Returns the lists of wallets a particular user has """
        data, wallets = [],{}
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT wallet_name, wallet_address FROM UserWallet WHERE user_id = ?',(user_id,))
        for i in cur:
            wallets["name"] = i[0]
            wallets["address"] =  i[1]
            data.append(wallets)
            wallets = {}
            
        conn.close()
        return(data)
        
    def user_exists(self,user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        sql_ = "SELECT EXISTS(SELECT * from UserInfo WHERE user_id=?);"
        cur.execute(sql_,(user_id,))
        result = cur.fetchone()[0]
        conn.close()
        if result == 0:
            return(False)
        return(True)
    
    def remove_passphrase(self, wallet_address):
        
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        sql_ = "UPDATE UserWallet SET wallet_phrase = NULL WHERE wallet_address = ?"
        
        cur.execute(sql_,(wallet_address,))
        conn.commit()
        conn.close()
        return
    
    def add_wallet_address(self,user_id,wallet_address,private_key):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        sql_ = "UPDATE UserWallet SET wallet_address = ? WHERE wallet_address = '0xWA' AND user_id = ?"
        cur.execute(sql_,(wallet_address,user_id,))
        conn.commit()
        sql_ = "UPDATE UserWallet SET private_key = ? WHERE wallet_address = ? AND user_id = ?"
        cur.execute(sql_,(private_key,wallet_address,user_id,))
        conn.commit()
        conn.close()
        return
    
    
    def most_recent_wallet(self,user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute(sort_wallet_by_date,(user_id,))
        result = cur.fetchone()
        conn.close()
        return(result)
    
    def current_wallet(self,user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT wallet_address FROM UserWallet WHERE user_id = ? AND current_wallet = 1',(user_id,))
        result = cur.fetchone()
        conn.close()
        return(result)
    
    def set_current_wallet(self,user_id, wallet_adrress):
        print(wallet_adrress,"hschsgcshcgshcg")
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        sql_ = f"UPDATE UserWallet SET current_wallet = 0 WHERE user_id = {user_id}"
        cur.execute(sql_)
        conn.commit()

        sql_ = f"UPDATE UserWallet SET current_wallet = 1 WHERE wallet_address = '{wallet_adrress}' AND user_id = {user_id}"
        cur.execute(sql_)
        conn.commit()

        conn.close()
        return

    def return_private_key(self, wallet_address):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT private_key FROM UserWallet WHERE wallet_address = ?',(wallet_address,))
        result = cur.fetchone()
        conn.close()
        return(result)
    
    def create_txn(self,user_id,coin_name,coin_amount):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('INSERT INTO UserTxns (txn_id,user_id,coin_name,coin_amount,date_created) VALUES (?,?,?,?,?)',(uuid.uuid1(),user_id,coin_name,coin_amount,datetime.now(),))
        conn.commit()
        conn.close()
        return
    
    def return_recent_txn(self,user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute(sort_txns_by_date,(user_id,))
        result = cur.fetchone()
        conn.close()
        return(result)
    
    def return_txn_data(self,txn_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT * FROM UserTxns WHERE txn_id = ?',(txn_id,))
        result = cur.fetchone()
        conn.close()
        return(result)
    
    def add_receiver_address(self,txn_id,reciever_address):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        sql_ = "UPDATE UserTxns SET reciever_address = ? WHERE txn_id = ?"
        cur.execute(sql_,(reciever_address,txn_id,))
        conn.commit()
        conn.close()
        return
    
    def add_amount_to_send(self,txn_id, amount):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        sql_ = "UPDATE UserTxns SET amount = ? WHERE txn_id = ?"
        cur.execute(sql_,(amount,txn_id,))
        conn.commit()
        conn.close()
        return
    
        


        

