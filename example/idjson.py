import argparse
import json
import pathlib

import pxsol

# Parses a local id.json file and converts it to a different format. The most useful output is in the "prikey/wif"
# format, which is what most browser wallets expect.

parser = argparse.ArgumentParser()
idjson = pathlib.Path.home().joinpath('.config/solana/id.json').as_posix()
parser.add_argument('--idjson', type=str, default=idjson, help='path to id.json')
args = parser.parse_args()

idjson = json.loads(pathlib.Path(args.idjson).read_text())
prikey = pxsol.core.PriKey(bytearray(idjson[:32]))
pubkey = pxsol.core.PubKey(bytearray(idjson[32:]))
assert prikey.pubkey() == pubkey

print('prikey/base58', prikey.base58())
print('prikey/hex   ', prikey.hex())
print('prikey/wif   ', prikey.wif())
print()
print('pubkey/base58', pubkey.base58())
print('pubkey/hex   ', pubkey.hex())
