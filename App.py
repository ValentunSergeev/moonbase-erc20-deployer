from flask import Flask, render_template, request
from web3 import Web3, HTTPProvider

app = Flask(__name__)

print("Loading web3...")

web3 = Web3(provider=HTTPProvider("https://rpc.testnet.moonbeam.network"))
web3.eth.account.enable_unaudited_hdwallet_features()
account = web3.eth.account.from_mnemonic("second wire page void maid example hazard record assist funny flower enough")

web3.eth.defaultAccount = account.address

with open("contract/abi") as fin:
    abi = fin.read()

with open("contract/bytecode") as fin:
    bytecode = fin.read()

contractTemplate = web3.eth.contract(abi=abi, bytecode=bytecode)


def deploy_new_contract(name, symbol, supply):
    construct_txn = contractTemplate.constructor(name, symbol, supply).buildTransaction({
        'from': account.address,
        'nonce': web3.eth.getTransactionCount(account.address),
        'gas': 4612388,
        'gasPrice': web3.toWei('21', 'gwei')
    })

    signed = account.signTransaction(construct_txn)

    return web3.eth.sendRawTransaction(signed.rawTransaction)


@app.route('/', methods=['get'])
def index():
    return render_template('index.html')


@app.route('/deploy', methods=['post'])
def deploy():
    name = request.form.get("name")
    symbol = request.form.get("symbol")
    supply = request.form.get("total_supply")

    tx_hash = web3.toHex(deploy_new_contract(name, symbol, int(supply)))
    tx_link = f"https://moonbase-blockscout.testnet.moonbeam.network/tx/{tx_hash}"

    print(tx_link)

    return render_template('deployed.html', name=name, symbol=symbol, supply=supply, tx_link=tx_link)


app.run(debug=True, port=5000)
