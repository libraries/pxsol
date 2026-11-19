import base64
import json

import pxsol

# An example script to fetch and display spl token mint information.

pxsol.config.current = pxsol.config.mainnet

for name, mint in pxsol.config.current.spl.items():
    info = pxsol.rpc.get_account_info(mint, {})
    info = pxsol.core.TokenMint.serialize_decode(bytearray(base64.b64decode(info['data'][0])))
    print(name, mint, json.dumps(info.json(), indent=4))
