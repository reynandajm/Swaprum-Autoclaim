import threading
from fake_useragent import UserAgent
import requests
import time
import random

from web3.auto import w3
from eth_account.messages import encode_defunct

#Isi dengan format seperti berikut addresses = ["Address Wallet:Private Key", "Address Wallet:Private Key"]
addresses = [""]

def main(address):
    time.sleep(random.randint(2,10))
    public = address.split(":")[0]
    private = address.split(":")[1]
    while True:
        balance = requests.get(f"https://swaprum.finance/server/user?address={public}")
        if int(balance.json()["freeClaimBalance"]) / 1000000000000000000 > 0.5:
            claim(public, private)
        response = requests.get('https://swaprum.finance/server/claim-free', params={"address": public}, headers={'user-agent': UserAgent().random})
        if "wait 1 hour" in response.text:
            print(f'{time.strftime("%H:%M:%S")} | {public} | {int(balance.json()["freeClaimBalance"]) / 1000000000000000000} | - Coba lagi 5 Menit kemudian.')
        elif "success" in response.text:
            print(f'{time.strftime("%H:%M:%S")} | {public} | {int(balance.json()["freeClaimBalance"])/1000000000000000000} | - Claim.')
        else:
            print(response.json())
        time.sleep(300)

def claim(public, private):

    message = encode_defunct(text=f"{public[-10:]}-free-claim-balance")
    get_signature = w3.eth.account.sign_message(message, f'{private}')
    signature = get_signature[4].hex()
    claim = requests.get(f"https://swaprum.finance/server/withdrawal?address={public}&type=free-claim&sig={signature}")

    if '{"success":true}' in claim.text:
        print(f'{time.strftime("%H:%M:%S")} | {public} | - Withdraw.')
    elif '{"error":"Minimal amount is 0.5"}' in claim.text:
        print(f'{time.strftime("%H:%M:%S")} | {public} | - Balance tidak cukup.')
    else:
        print(claim.text)

if __name__ == "__main__":
    print(f'{time.strftime("%H:%M:%S")} | Account: {len(addresses)}')
    for address in addresses:
        public = address.split(":")[0]
        private = address.split(":")[1]
        thread = threading.Thread(target=main, args=(address,))
        thread.start()