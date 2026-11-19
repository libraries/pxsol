import argparse

import pxsol

# Transfer sol to other.

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, help='private key')
parser.add_argument('--to', type=str, help='to address')
parser.add_argument('--value', type=float, help='sol value')
args = parser.parse_args()

if args.net == 'develop':
    pxsol.config.current = pxsol.config.develop
if args.net == 'mainnet':
    pxsol.config.current = pxsol.config.mainnet
if args.net == 'testnet':
    pxsol.config.current = pxsol.config.testnet
pxsol.config.current.log = 1

user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(int(args.prikey, 0)))
hole = pxsol.core.PubKey.base58_decode(args.to)
user.sol_transfer(hole, int(args.value * pxsol.denomination.sol))
