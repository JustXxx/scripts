import sys
import csv
from web3 import Web3
from eth_account import Account

def load_wallets_from_csv(filename):
    wallets = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header row
        for row in csvreader:
            if len(row) != 2:
                continue
            address, amount = row
            wallets.append((address, Web3.toWei(float(amount), 'ether')))
    return wallets

def batch_transfer_eth(private_key, wallets, network):
    if network == 'mainnet':
        w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'))
    elif network == 'holesky':
        w3 = Web3(Web3.HTTPProvider('https://holesky.infura.io/v3/YOUR_INFURA_PROJECT_ID'))
    elif network == 'testnet':
        w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/YOUR_INFURA_PROJECT_ID'))
    else:
        print("Unsupported network. Please choose 'mainnet', 'holesky', or 'testnet'.")
        sys.exit(1)

    account = Account.from_key(private_key)
    nonce = w3.eth.getTransactionCount(account.address)

    for address, amount in wallets:
        tx = {
            'nonce': nonce,
            'to': address,
            'value': amount,
            'gas': 21000,
            'gasPrice': w3.eth.gas_price,
        }
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(f"Transaction sent to {address} with hash: {tx_hash.hex()}")
        nonce += 1

def main():
    if len(sys.argv) != 4:
        print("Usage: python batch_transfer_eth.py <private_key> <csv_file_path> <network>")
        sys.exit(1)

    private_key = sys.argv[1]
    csv_file_path = sys.argv[2]
    network = sys.argv[3]

    wallets = load_wallets_from_csv(csv_file_path)
    batch_transfer_eth(private_key, wallets, network)

if __name__ == "__main__":
    main()
