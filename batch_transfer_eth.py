import sys
import csv
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_wallets_from_csv(filename):
    wallets = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header row
        for row in csvreader:
            if len(row) != 3:
                continue
            address, _, amount = row  # Ignore the second column
            wallets.append((address, Web3.to_wei(float(amount), 'ether')))
    return wallets

def batch_transfer_eth(wallets, network):
    infura_project_id = os.getenv('INFURA_PROJECT_ID')
    private_key = os.getenv('PRIVATE_KEY')

    if not infura_project_id:
        logging.error("Infura project ID not found in .env file.")
        sys.exit(1)

    if not private_key:
        logging.error("Private key not found in .env file.")
        sys.exit(1)

    if network == 'mainnet':
        w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{infura_project_id}'))
        chain_id = 1
    elif network == 'holesky':
        w3 = Web3(Web3.HTTPProvider(f'https://holesky.infura.io/v3/{infura_project_id}'))
        chain_id = 17000  # 假设 Holesky 的链ID是17000，请根据实际情况调整
    elif network == 'testnet':
        w3 = Web3(Web3.HTTPProvider(f'https://goerli.infura.io/v3/{infura_project_id}'))
        chain_id = 5
    else:
        logging.error("Unsupported network. Please choose 'mainnet', 'holesky', or 'testnet'.")
        sys.exit(1)

    account = Account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    # Display initial balance
    initial_balance = w3.eth.get_balance(account.address)
    logging.info(f"Initial balance of sender: {Web3.from_wei(initial_balance, 'ether')} ETH")

    # Log the number of wallets
    logging.info(f"Number of wallets to transfer: {len(wallets)}")

    for address, amount in wallets:
        try:
            tx = {
                'nonce': nonce,
                'to': address,
                'value': amount,
                'gas': 21000,
                'gasPrice': w3.eth.gas_price,
                'chainId': chain_id
            }
            signed = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            logging.info(f"Transaction sent to {address} with hash: {tx_hash.hex()}")
            nonce += 1
        except Exception as e:
            logging.error(f"Failed to send transaction to {address}: {str(e)}")

    # Display final balance
    final_balance = w3.eth.get_balance(account.address)
    logging.info(f"Final balance of sender: {Web3.from_wei(final_balance, 'ether')} ETH")

def main():
    if len(sys.argv) != 3:
        logging.error("Usage: python batch_transfer_eth.py <csv_file_path> <network>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    network = sys.argv[2]

    wallets = load_wallets_from_csv(csv_file_path)
    batch_transfer_eth(wallets, network)

if __name__ == "__main__":
    main()
