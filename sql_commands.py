
create_table_users = """

CREATE TABLE IF NOT EXISTS UserInfo (
	user_id INTEGER UNIQUE,
	date_joined timestamp
);
"""

create_table_wallets = """
CREATE TABLE IF NOT EXISTS UserWallet (
	user_id INTEGER,
	wallet_name TEXT,
	wallet_address TEXT NOT NULL,
	wallet_phrase TEXT,
	private_key TEXT,
	date_created timestamp,
	current_wallet INTEGER,
	PRIMARY KEY (wallet_address),
	FOREIGN KEY (user_id) REFERENCES UserInfo (user_id)
);
"""


create_table_txn_history = """
CREATE TABLE IF NOT EXISTS UserTxns (
	txn_id GUID,
	user_id INTEGER,
	coin_name TEXT NOT NULL,
	reciever_address TEXT,
	coin_amount REAL,
	amount REAL,
	date_created timestamp,
	PRIMARY KEY (txn_id)
);

"""



sort_wallet_by_date = """
SELECT *
FROM UserWallet WHERE user_id = ?
ORDER BY date_created DESC;
"""

sort_txns_by_date = """
SELECT *
FROM UserTxns WHERE user_id = ?
ORDER BY date_created DESC;
"""


        