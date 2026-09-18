import argparse
import base64
import pathlib
import pxsol

# Deploy a hello solana program, call it to show "Hello, Solana!". Then we update the program and call it again, it
# will display another welcome message. Finally, we close the program to withdraw all solanas.

parser = argparse.ArgumentParser()
parser.add_argument('--action', type=str, choices=['call', 'closed', 'deploy', 'update'])
parser.add_argument('--addr', type=str, help='addr')
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, help='private key')
args = parser.parse_args()

if args.net == 'develop':
    pxsol.config.current = pxsol.config.develop
if args.net == 'mainnet':
    pxsol.config.current = pxsol.config.mainnet
if args.net == 'testnet':
    pxsol.config.current = pxsol.config.testnet
pxsol.config.current.log = 1

user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(int(args.prikey, 0)))

if args.action == 'call':
    rq = pxsol.core.Requisition(pxsol.core.PubKey.base58_decode(args.addr), [], bytearray())
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)

if args.action == 'closed':
    pubkey = pxsol.core.PubKey.base58_decode(args.addr)
    user.program_closed(pubkey)
    print('Program', pubkey, 'closed')

if args.action == 'deploy':
    data = bytearray(pathlib.Path('res/program_1.so').read_bytes())
    pubkey = user.program_deploy(data)
    print('Program', pubkey, 'create')

if args.action == 'update':
    data = bytearray(pathlib.Path('res/program_2.so').read_bytes())
    pubkey = pxsol.core.PubKey.base58_decode(args.addr)
    user.program_update(pubkey, data)
    print('Program', pubkey, 'update')
