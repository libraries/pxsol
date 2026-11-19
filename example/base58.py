import argparse

import pxsol

# Base58 encode or decode hex string.

parser = argparse.ArgumentParser()
parser.add_argument('--decode', type=str, help='decode data')
parser.add_argument('--encode', type=str, help='encode data')
args = parser.parse_args()

if args.decode:
    print(pxsol.base58.decode(args.decode).hex())

if args.encode:
    print(pxsol.base58.encode(bytearray.fromhex(args.encode)))
