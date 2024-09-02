import os
import concurrent.futures
import logging
from web3 import Web3
from eth_account import Account

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# Serial number for log messages
serial_number = 1

# Define Watchdata and Blast API keys for Ethereum, BSC, and Polygon
eth_watchdata_api_key = "066ef05b-8c44-43a6-b281-e518617cd242"
eth_blast_api_key = "c164c92f-2c6a-4f31-a8ca-1f02e984c2ec"
bsc_watchdata_api_key = "1cc1f9cd-a996-4e47-b533-e7a5c1760372"
bsc_blast_api_key = "c164c92f-2c6a-4f31-a8ca-1f02e984c2ec"
polygon_watchdata_api_key = "93767cd2-6087-4027-969f-07f78ceb34c5"
polygon_blast_api_key = "c164c92f-2c6a-4f31-a8ca-1f02e984c2ec"

def generate_mnemonic_phrase():
    """
    Generates a 12-word mnemonic phrase using eth_account's create_with_mnemonic function.

    Returns:
    - str: The generated mnemonic phrase.
    """
    account, mnemonic = Account.create_with_mnemonic()
    return mnemonic

def check_balance(mnemonic_phrase, watchdata_api_key, blast_api_key, blockchain):
    """
    Checks the balance of the main wallet associated with a given mnemonic phrase.

    Parameters:
    - mnemonic_phrase: str
        The 12-word mnemonic phrase.
    - watchdata_api_key: str
        The Watchdata API key for the blockchain.
    - blast_api_key: str
        The Blast API key for the blockchain.
    - blockchain: str
        The blockchain being checked (Ethereum, BSC, or Polygon).

    Returns:
    - float: The balance of the main wallet in Ether (for Ethereum), BNB (for BSC), MATIC (for Polygon), or None if no balance.
    """
    try:
        # Select API based on the serial number
        if serial_number % 2 == 0:
            api_key = watchdata_api_key
            if blockchain == "Ethereum":
                api_url = f"https://ethereum.api.watchdata.io/node/jsonrpc?api_key={api_key}"
            elif blockchain == "BSC":
                api_url = f"https://bsc.api.watchdata.io/node/jsonrpc?api_key={api_key}"
            elif blockchain == "Polygon":
                api_url = f"https://polygon.api.watchdata.io/node/jsonrpc?api_key={api_key}"
        else:
            api_key = blast_api_key
            if blockchain == "Ethereum":
                api_url = f"https://eth-mainnet.blastapi.io/{api_key}"
            elif blockchain == "BSC":
                api_url = f"https://bsc-mainnet.blastapi.io/{api_key}"
            elif blockchain == "Polygon":
                api_url = f"https://polygon-mainnet.blastapi.io/{api_key}"

        web3 = Web3(Web3.HTTPProvider(api_url))

        # Derive the account from the mnemonic phrase
        account = Account.from_mnemonic(mnemonic_phrase)

        # Get the main wallet address
        main_wallet_address = account.address

        # Check the balance of the main wallet
        balance = web3.eth.get_balance(main_wallet_address)
        if blockchain == "Polygon":
            return web3.fromWei(balance, "ether") if balance > 0 else None
        else:
            return web3.fromWei(balance, "ether") if balance > 0 else None
    except Exception as e:
        logger.error(f"Error checking {blockchain} balance for mnemonic phrase: {e}")
        return None

def save_mnemonic_phrase(mnemonic_phrase, blockchain, balance):
    """
    Saves the mnemonic phrase and balance to a file.

    Parameters:
    - mnemonic_phrase: str
        The 12-word mnemonic phrase.
    - blockchain: str
        The blockchain being checked.
    - balance: float
        The balance of the wallet.
    """
    filename = f"wallet_with_balance_{blockchain.lower()}.txt"
    with open(filename, "a") as f:
        f.write("Mnemonic Phrase: " + mnemonic_phrase + "\n")
        f.write("Blockchain: " + blockchain + "\n")
        f.write("Balance: " + str(balance) + "\n")
        f.write("\n")
    logger.info(f"Found wallet with balance for {blockchain}: {balance}")

def find_wallet_with_balance():
    """
    Continuously generates mnemonic phrases and checks balances until a positive balance above the minimum threshold is found.
    """
    global serial_number

    while True:
        mnemonic_phrase = generate_mnemonic_phrase()
        eth_balance = check_balance(mnemonic_phrase, eth_watchdata_api_key, eth_blast_api_key, "Ethereum")
        if eth_balance:
            logger.info(f"[{serial_number}] Balance: {eth_balance} (Ethereum) | Wallet checked: ({mnemonic_phrase})")
            save_mnemonic_phrase(mnemonic_phrase, "Ethereum", eth_balance)
            return
        bsc_balance = check_balance(mnemonic_phrase, bsc_watchdata_api_key, bsc_blast_api_key, "BSC")
        if bsc_balance:
            logger.info(f"[{serial_number}] Balance: {bsc_balance} (BSC) | Wallet checked: ({mnemonic_phrase})")
            save_mnemonic_phrase(mnemonic_phrase, "BSC", bsc_balance)
            return
        polygon_balance = check_balance(mnemonic_phrase, polygon_watchdata_api_key, polygon_blast_api_key, "Polygon")
        if polygon_balance:
            logger.info(f"[{serial_number}] Balance: {polygon_balance} (Polygon) | Wallet checked: ({mnemonic_phrase})")
            save_mnemonic_phrase(mnemonic_phrase, "Polygon", polygon_balance)
            return
        logger.info(f"[{serial_number}] Balance: 0 | Wallet checked: ({mnemonic_phrase})")
        serial_number += 1

if __name_ == "_main__":
    # Enable Mnemonic features
    Account.enable_unaudited_hdwallet_features()

    # Run the search for a wallet with balance
    find_wallet_with_balance()