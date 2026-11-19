import argparse
import base64

import pxsol

# This is an example centered around solana tokens. You can create a brand-new token, mint fresh tokens, and send them
# as gifts to your friends.

parser = argparse.ArgumentParser()
parser.add_argument('--action', type=str, choices=['balance', 'create', 'mint', 'transfer'])
parser.add_argument('--decimals', type=int, default=9, help='token decimals')
parser.add_argument('--name', type=str, help='token name')
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--symbol', type=str, help='token symbol')
parser.add_argument('--token', type=str, help='token addr')
parser.add_argument('--uri', type=str, help='token uri')
parser.add_argument('--prikey', type=str, help='private key')
parser.add_argument('--to', type=str, help='to address')
parser.add_argument('--amount', type=float, help='token amount')
args = parser.parse_args()

if args.net == 'develop':
    pxsol.config.current = pxsol.config.develop
if args.net == 'mainnet':
    pxsol.config.current = pxsol.config.mainnet
if args.net == 'testnet':
    pxsol.config.current = pxsol.config.testnet
pxsol.config.current.log = 1

user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(int(args.prikey, 0)))

if args.action == 'balance':
    mint = pxsol.core.PubKey.base58_decode(args.token)
    r = user.spl_balance(mint)
    print(r[0] / 10 ** r[1])

if args.action == 'create':
    mint = user.spl_create(args.decimals, {
        'metadata': {
            'name': args.name,
            'symbol': args.symbol,
            'uri': args.uri,
        }
    })
    print(mint.base58())

if args.action == 'mint':
    mint = pxsol.core.PubKey.base58_decode(args.token)
    mint_result = pxsol.rpc.get_account_info(mint.base58(), {})
    mint_info = pxsol.core.TokenMint.serialize_decode(bytearray(base64.b64decode(mint_result['data'][0])))
    user.spl_mint(
        pxsol.core.PubKey.base58_decode(args.token),
        user.pubkey,
        int(args.amount * 10 ** mint_info.decimals),
    )

if args.action == 'transfer':
    mint = pxsol.core.PubKey.base58_decode(args.token)
    mint_result = pxsol.rpc.get_account_info(mint.base58(), {})
    mint_info = pxsol.core.TokenMint.serialize_decode(bytearray(base64.b64decode(mint_result['data'][0])))
    user.spl_transfer(
        pxsol.core.PubKey.base58_decode(args.token),
        pxsol.core.PubKey.base58_decode(args.to),
        int(args.amount * 10 ** mint_info.decimals),
    )
