# Pxsol: Solana Library For Humans

Pxsol is a project that aims to provide human-friendly interfaces for common Solana operations. It's zero-dependency and pure-python, providing a secure and simple way to interact with the Solana network. Whether you're a beginner looking to learn about Solana or an experienced developer seeking a straightforward library, pxsol has got you covered.

## Installation

```sh
$ pip install pxsol
# or
$ git clone https://github.com/libraries/pxsol
$ cd pxsol
$ python -m pip install --editable .
```

## Documentation and Courses

![img](./doc/en/markdown/img/cover.jpg)

**Read or download the book via the following link**

- [English - Markdown](https://github.com/libraries/pxsol/tree/master/doc/en/markdown)
- [English - PDF](https://github.com/libraries/pxsol/releases/download/v1.1.4/pxsol-en.pdf)
- [English - Web](https://pxsol.vercel.app/)
- [中文 - Markdown](https://github.com/libraries/pxsol/tree/master/doc/zh/markdown)
- [中文 - PDF](https://github.com/libraries/pxsol/releases/download/v1.1.4/pxsol-zh.pdf)
- [中文 - Web](http://accu.cc/content/solana/foreword/)

## Usage

By default, pxsol is configured on the develop. To switch the network to the main network, use the following code:

```py
import pxsol
pxsol.config.current = pxsol.config.mainnet
```

**example/addr.py**

Calculate the address from a private key.

Solana's private key is a 32-byte array, selected arbitrarily. In general, the private key is not used in isolation instead, it forms a 64-byte keypair together with the public key, which is also a 32-byte array. Most solana wallets, such as phantom, import and export private keys in base58-encoded keypair format.

In this example, we use u256 to represent a 32-byte private key.

```sh
$ python example/addr.py --prikey 0x1

# 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
```

**example/balance.py**

Get the balance by an address.

```sh
$ python example/balance.py --net develop --addr 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt

# 10000

$ python example/balance.py --net mainnet --addr 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt

# 0.002030181
```

**example/base58.py**

Base58 encode or decode hex string.

```sh
$ python example/base58.py --decode 3Bxs46DNLk1oRbZR

# 020000002007150000000000

$ python example/base58.py --encode 020000002007150000000000

# 3Bxs46DNLk1oRbZR
```

**example/genesis.py**

Shows the accounts in the mainnet genesis block and their sol allocations.

```sh
$ python example/genesis.py

# APnSR52EC1eH676m7qTBHUJ1nrGpHYpV7XKPxgRDD8gX 162509534.46
# 13LeFbG6m2EP1fqCj9k66fcXsoTHMMtgr7c78AivUrYD 153333633.39
# GK2zqSsXLA2rwVZk347RYhh6jJpRsCA69FjLW93ZGi3B  57499999.98
# 8HVqyX9jebh31Q9Hp8t5sMVJs665979ZeEr3eCfzitUe  30301031.98
# HbZ5FfmKWNHC7uwk6TF1hVi6TCs7dtYfdjEcuPGgzFAg  14999999.98
# ...
```

**example/history.py**

Shows the most recent transactions for an address.

```sh
$ python example/history.py --addr 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt --limit 1

# {'signatures': ['5aAPZipgfGVPSuz2wdSg5hNFbudnELjCKYLRap6o...
```

**example/idjson.py**

Parses a local `id.json` file and converts it to a different format. The most useful output is in the `prikey/wif` format, which is what most browser wallets expect.

```sh
$ python example/idjson.py --idjson res/id.json

# prikey/base58 11111111111111111111111111111112
# prikey/hex    0000000000000000000000000000000000000000000000000000000000000001
# prikey/wif    1111111111111111111111111111111PPm2a2NNZH2EFJ5UkEjkH9Fcxn8cvjTmZDKQQisyLDmA

# pubkey/base58 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
# pubkey/hex    4cb5abf6ad79fbf5abbccafcc269d85cd2651ed4b885b5869f241aedf0a5ba29
```

**example/program.py**

Deploy a hello solana program, call it to show "Hello, Solana!". Then we update the program and call it again, it will display another welcome message. Finally, we close the program to withdraw all solanas.

```sh
$ python example/program.py --prikey 0x1 --action deploy
# Program 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG create

$ python example/program.py --prikey 0x1 --action call --addr 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG
# Program 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG invoke [1]
# Program log: Hello, Solana!
# Program log: Our program's Program ID: 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG
# Program 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG consumed 11850 of 200000 compute units
# Program 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG success

$ python example/program.py --prikey 0x1 --action update --addr 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG
# Program 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG update

$ python example/program.py --prikey 0x1 --action call --addr 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG
# Program 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG invoke [1]
# Program log: Hello, Solana! Hello Update!
# Program log: Our program's Program ID: 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG
# Program 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG consumed 11850 of 200000 compute units
# Program 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG success

$ python example/program.py --prikey 0x1 --action closed --addr 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG
# Program 6B7KVuUQ42x8SagFuFaoiV9jWTSic3Qd771kNrmGwoBG closed
```

**example/pxs_airdrop.py**

Apply for PXS airdrop on the mainnet. PXS is a token issued by pxsol for teaching purposes, and anyone can claim it.

Mint address: `6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH`

```sh
$ python example/pxs_airdrop.py --prikey 0xYOUR_MAINNET_PRIVATE_KEY
```

You can choose to keep the airdrop, or sell it to get sol. Swap: <https://raydium.io/swap/?inputMint=6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH&outputMint=sol>

**example/spl_info.py**

An example script to fetch and display spl token mint information.

```sh
$ python example/spl_info.py

# usdc EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v {
#     "auth_mint": "BJE5MMbqXjVwjAF7oxwPYXnTXDyspzZyt4vwenNw5ruG",
#     "supply": 8710696113418469,
#     "decimals": 6,
#     "inited": true,
#     "auth_freeze": "7dGbd2QZcCKcTndnHcTL8q7SMVXAkp688NTQYwrRCrar",
#     "extensions": {}
# }
# usdt Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB {
#     "auth_mint": "Q6XprfkF8RQQKoQVG33xT88H7wi8Uk1B1CC7YAs69Gi",
#     "supply": 2739917003349244,
#     "decimals": 6,
#     "inited": true,
#     "auth_freeze": "Q6XprfkF8RQQKoQVG33xT88H7wi8Uk1B1CC7YAs69Gi",
#     "extensions": {}
# }
```

**example/spl.py**

This is an example centered around solana tokens. You can create a brand-new token, mint fresh tokens, and send them as gifts to your friends.

```sh
# Create a new token.
$ python example/spl.py --prikey 0x1 --action create --name PXSOL --symbol PXS --uri https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/pxs.json
# H5qBQeMh2YYagEbQSvPdEeojwcn7Bg9g6W5ifTJzB7HG

# Mint 100 tokens for your self.
$ python example/spl.py --prikey 0x1 --token H5qBQeMh2YYagEbQSvPdEeojwcn7Bg9g6W5ifTJzB7HG --action mint --amount 100

# Display your token balance.
$ python example/spl.py --prikey 0x1 --token H5qBQeMh2YYagEbQSvPdEeojwcn7Bg9g6W5ifTJzB7HG --action balance

# Transfer 20 token to other.
$ python example/spl.py --prikey 0x1 --token H5qBQeMh2YYagEbQSvPdEeojwcn7Bg9g6W5ifTJzB7HG --action transfer --to 8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH --amount 20
```

**example/transfer.py**

Transfer sol to other.

```sh
$ python example/transfer.py --prikey 0x1 --to 8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH --value 0.05

# 4GhcAygac8krnrJgF2tCSNxRyWsquCZ26NPM6o9oP3bPQFkAzi22CGn9RszBXzqPErujVxwzenTHoTMHuiZm98Wu
```

**example/wif.py**

Calculate the wallet import format from the private key. This is useful when you are trying to import an account in phantom wallet.

```sh
$ python example/wif.py --prikey 0x1

# 1111111111111111111111111111111PPm2a2NNZH2EFJ5UkEjkH9Fcxn8cvjTmZDKQQisyLDmA
```

## Test

```sh
$ wget https://github.com/anza-xyz/agave/releases/download/v3.1.8/solana-release-x86_64-unknown-linux-gnu.tar.bz2
$ tar -xvf solana-release-x86_64-unknown-linux-gnu.tar.bz2
$ cd solana-release

# Run test validator
$ solana-test-validator -l /tmp/solana-ledger
$ solana config set --url localhost
$ solana airdrop 99 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt

$ pytest -v
```

## License

MIT
