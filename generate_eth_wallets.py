import sys
import csv
from datetime import datetime
from eth_account import Account

def generate_wallets(num_wallets):
    wallets = []
    for _ in range(num_wallets):
        account = Account.create()
        wallets.append((account.address, account.key.hex()))
    return wallets

def save_wallets_to_csv(wallets, filename):
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Address', 'Private Key'])
        csvwriter.writerows(wallets)

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_eth_wallets.py <number_of_wallets>")
        sys.exit(1)

    try:
        num_wallets = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid number for the number of wallets.")
        sys.exit(1)

    if num_wallets <= 0:
        print("The number of wallets must be a positive integer.")
        sys.exit(1)

    wallets = generate_wallets(num_wallets)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"eth_wallets_{timestamp}.csv"
    save_wallets_to_csv(wallets, filename)
    print(f"Generated {num_wallets} wallets and saved to {filename}")

if __name__ == "__main__":
    main()
