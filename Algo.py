
import time
from datetime import datetime
from algosdk.future.transaction import PaymentTxn
from algosdk.v2client import algod
from algosdk.v2client import indexer
from algosdk import account, mnemonic

algod_address = "https://testnet-algorand.api.purestake.io/ps2" 
indexer_address = "https://testnet-algorand.api.purestake.io/idx2"
algod_token = "🔑"
headers = {
    "X-API-Key": algod_token, # api key
}
algod_client = algod.AlgodClient(algod_token, algod_address, headers)
indexer_client = indexer.IndexerClient("", indexer_address, headers)

params = algod_client.suggested_params()
params.flat_fee = True
params.fee = 1000

def timestamp_to_string(timestamp):
    """ converts a timestamp to a string"""
    dt_obj = datetime.fromtimestamp(timestamp)
    date_time = dt_obj.strftime("%d/%m/%Y, %H:%M:%S")
    return date_time

def find_amount_W_decimal(amount, decimals):
    result = '{:.19f}'.format(amount * 10**-decimals)
    return float(result)


def generate_algorand_account(name): # ✅
    private_key, address = account.generate_account()
    wallet_passphrase = mnemonic.from_private_key(private_key)
    account_dict = {}
    account_dict['name'] = name
    account_dict['address'] = address
    account_dict['phrase'] = wallet_passphrase
    account_dict['key'] = private_key
    return account_dict

def show_wallet_address(phrase):
    wallet_address = mnemonic.to_public_key(phrase)
    return wallet_address

def show_private_key(phrase):
    key = mnemonic.to_private_key(phrase)
    return(key)
    
    
def show_account_in_explorer(wallet_address):
    msg = f"https://testnet.algoexplorer.io/address/{wallet_address}"
    return msg

def show_transaction_in_explorer(txid):
    msg = f"https://testnet.algoexplorer.io/tx/{txid}"
    return msg

def show_asset_in_explorer(asset_id):
    msg = f"https://testnet.algoexplorer.io/asset/{asset_id}"
    return msg

def wallet_holdings(wallet_address): #✅
    asset_list = []
    response = indexer_client.account_info(address=wallet_address)
    
    
    try:
        address = response['account']['address']
    except KeyError:
        return(response)
    algo_amount = find_amount_W_decimal(response['account']['amount'], 6)
    algo_amount_without_pending_rewards = find_amount_W_decimal(response['account']['amount-without-pending-rewards'], 6)
    
    asset_holdings = {}
    asset_holdings['address'] = address
    asset_holdings['algo_amount'] = algo_amount
    asset_holdings['algo_amount_without_pending_rewards'] = algo_amount_without_pending_rewards

    
    if 'assets' in response['account']:
        assets = response['account']['assets']
        for asset in assets:
            time.sleep(1)
            amount = asset['amount']
            is_frozen = asset['is-frozen']

            asset_id = asset['asset-id']

            asset_data = indexer_client.search_assets(asset_id=asset_id, limit=len(assets))
            coins = asset_data['assets']
            for coin in coins:
                asset_name = coin['params']['name']
                asset_unit =coin['params']['unit-name']
                decimal =coin['params']['decimals']

                asset_amount = find_amount_W_decimal(amount, decimal)
            
                asset_dict = {}
                asset_dict['name'] = asset_name
                asset_dict['unit'] = asset_unit
                asset_dict['id'] = asset_id
                asset_dict['amount'] = amount
                asset_dict['amount_w_decimal'] = asset_amount
                asset_dict['decimal'] = decimal
                asset_dict['frozen'] = is_frozen

                asset_list.append(asset_dict)
    asset_holdings['assets'] = asset_list
    return asset_holdings

def recent_algo_transactions(wallet_address): # ✅
    transactions_dict = {}
    sent = []
    received = []
    response = indexer_client.search_transactions_by_address(wallet_address, txn_type='pay')
    pay_transactions = response['transactions']
    if pay_transactions == []:
        pass
    else:
        for transaction in pay_transactions:
            transact = {}
            transact['sender'] = transaction['sender']
            transact['receiver'] = transaction['payment-transaction']['receiver']
            transact['amount'] = transaction['payment-transaction']['amount']
            transact['amount_w_decimal'] = find_amount_W_decimal(transaction['payment-transaction']['amount'], 6)
            transact['fee'] = transaction['fee']
            transact['txid'] = transaction['id']
            transact['tx_time'] = timestamp_to_string(transaction['round-time'])
            transact['tx_type'] = transaction['tx-type']
            if transact['sender'] == wallet_address:
                sent.append(transact)
            elif transact['sender'] != wallet_address:
                received.append(transact)
        transactions_dict['sent'] = sent
        transactions_dict['received'] =  received
        return transactions_dict

def algo_balance(wallet_address): # ✅
    response = indexer_client.account_info(address=wallet_address)
    algo_amount = find_amount_W_decimal(response['account']['amount'], 6)
    return algo_amount

def send_algo(sender_address, receiver_address, amount, sender_key):
    txn = PaymentTxn(sender_address, params, receiver_address, amount)
    stxn = txn.sign(sender_key)
    txid = algod_client.send_transaction(stxn)
    transactioninfo = {}
    transactioninfo['txid'] = txid
    transactioninfo['link'] = f"https://testnet.algoexplorer.io/tx/{txid}"
    return transactioninfo





