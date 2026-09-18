import argparse
import base64
import pxsol

# Shows the last transactions for a address.

parser = argparse.ArgumentParser()
parser.add_argument('--addr', type=str, help='address')
parser.add_argument('--limit', type=int, help='limit count', default=1)
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
args = parser.parse_args()

if args.net == 'develop':
    pxsol.config.current = pxsol.config.develop
if args.net == 'mainnet':
    pxsol.config.current = pxsol.config.mainnet
if args.net == 'testnet':
    pxsol.config.current = pxsol.config.testnet

for e in pxsol.rpc.get_signatures_for_address(args.addr, {'limit': args.limit}):
    tx_meta = pxsol.rpc.get_transaction(e['signature'], {'encoding': 'base64'})
    tx_byte = bytearray(base64.b64decode(tx_meta['transaction'][0]))
    tx_verb = pxsol.core.TransactionClassify.version(tx_byte)
    match tx_verb:
        case 0x80:
            tx = pxsol.core.TransactionV0.serialize_decode(tx_byte)
            print(tx)
        case 0x81:
            tx = pxsol.core.TransactionV1.serialize_decode(tx_byte)
            print(tx)
        case _:
            tx = pxsol.core.Transaction.serialize_decode(tx_byte)
            print(tx)
