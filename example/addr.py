import argparse

import pxsol

# Calculate the address from a private key.
#
# Solana's private key is a 32-byte array, selected arbitrarily. In general, the private key is not used in isolation;
# instead, it forms a 64-byte keypair together with the public key, which is also a 32-byte array. Most solana wallets,
# such as phantom, import and export private keys in base58-encoded keypair format.
#
# In this example, we use u256 to represent a 32-byte private key.

parser = argparse.ArgumentParser()
parser.add_argument('--prikey', type=str, help='private key')
args = parser.parse_args()

prikey = pxsol.core.PriKey.int_decode(int(args.prikey, 0))
pubkey = prikey.pubkey()
addr = pubkey.base58()
print(addr)
