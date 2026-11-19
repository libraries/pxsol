import base64

import pxsol


def test_address_lookup_table():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
    slot = pxsol.rpc.get_slot({'commitment': 'finalized'})
    alta = pxsol.program.AddressLookupTable.pubkey.derive_pda(user.pubkey.p + bytearray(slot.to_bytes(8, 'little')))
    # Create address lookup table.
    r0 = pxsol.core.Requisition(pxsol.program.AddressLookupTable.pubkey, [], bytearray())
    r0.account.append(pxsol.core.AccountMeta(alta[0], 1))
    r0.account.append(pxsol.core.AccountMeta(user.pubkey, 2))
    r0.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    r0.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    r0.data = pxsol.program.AddressLookupTable.create_lookup_table(slot, alta[1])
    # Extend address lookup table.
    r1 = pxsol.core.Requisition(pxsol.program.AddressLookupTable.pubkey, [], bytearray())
    r1.account.append(pxsol.core.AccountMeta(alta[0], 1))
    r1.account.append(pxsol.core.AccountMeta(user.pubkey, 2))
    r1.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    r1.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    r1.data = pxsol.program.AddressLookupTable.extend_lookup_table([user.pubkey])
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [r0, r1])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
