import hashlib
import io
import json
import pxsol.base58
import pxsol.compact_u16
import pxsol.eddsa
import secrets
import typing


class PriKey:
    # Solana's private key is a 32-byte array, selected arbitrarily. In general, the private key is not used in
    # isolation; instead, it forms a 64-byte keypair together with the public key, which is also a 32-byte array.
    # Most solana wallets, such as phantom, import and export private keys in base58-encoded keypair format.

    def __init__(self, p: bytearray) -> None:
        assert isinstance(p, bytearray)
        assert len(p) == 32
        self.p = p

    def __eq__(self, other) -> bool:
        return self.p == other.p

    def __hash__(self) -> int:
        return self.int()

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def base58(self) -> str:
        # Convert the private key to base58 representation.
        return pxsol.base58.encode(self.p)

    @classmethod
    def base58_decode(cls, data: str) -> PriKey:
        # Convert the base58 representation to private key.
        return PriKey(pxsol.base58.decode(data))

    def hex(self) -> str:
        # Convert the private key to hex representation.
        return self.p.hex()

    @classmethod
    def hex_decode(cls, data: str) -> PriKey:
        # Convert the hex representation to private key.
        return PriKey(bytearray.fromhex(data))

    def int(self) -> int:
        # Convert the private key to u256 number, in big endian.
        return int.from_bytes(self.p)

    @classmethod
    def int_decode(cls, data: int) -> PriKey:
        # Convert the u256 number to private key, in big endian.
        return PriKey(bytearray(data.to_bytes(32)))

    def json(self) -> str:
        return self.base58()

    def pubkey(self) -> PubKey:
        # Get the eddsa public key corresponding to the private key.
        return PubKey(pxsol.eddsa.pubkey(self.p))

    @classmethod
    def random(cls) -> PriKey:
        return PriKey(bytearray(secrets.token_bytes(32)))

    def sign(self, data: bytearray) -> bytearray:
        # Sign a message of arbitrary length. Unlike secp256k1, the resulting signature is deterministic.
        return pxsol.eddsa.sign(self.p, data)

    def wif(self) -> str:
        # Convert the private key to wallet import format. This is the format supported by most third-party wallets.
        pubkey = self.pubkey()
        return pxsol.base58.encode(self.p + pubkey.p)

    @classmethod
    def wif_decode(cls, data: str) -> PriKey:
        # Convert the wallet import format to private key. This is the format supported by most third-party wallets.
        pripub = pxsol.base58.decode(data)
        prikey = PriKey(pripub[:32])
        pubkey = PubKey(pripub[32:])
        assert prikey.pubkey() == pubkey
        return prikey


class PubKey:
    # Solana's public key is a 32-byte array. The base58 representation of the public key is also referred to as the
    # address.

    def __init__(self, p: bytearray) -> None:
        assert isinstance(p, bytearray)
        assert len(p) == 32
        self.p = p

    def __eq__(self, other) -> bool:
        return self.p == other.p

    def __hash__(self) -> int:
        return self.int()

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def base58(self) -> str:
        # Convert the public key to base58 representation.
        return pxsol.base58.encode(self.p)

    @classmethod
    def base58_decode(cls, data: str) -> PubKey:
        # Convert the base58 representation to public key.
        return PubKey(pxsol.base58.decode(data))

    def derive(self, seed: bytearray, host: PubKey) -> PubKey:
        # Create new pubkey with seed and host.
        data = bytearray()
        data.extend(self.p)
        data.extend(seed)
        data.extend(host.p)
        assert not data.endswith(bytearray('ProgramDerivedAddress'.encode()))
        return PubKey(bytearray(hashlib.sha256(data).digest()))

    def derive_pda(self, seed: bytearray) -> tuple[PubKey, int]:
        # Program Derived Address (PDA). PDAs are addresses derived deterministically using a combination of
        # user-defined seeds, a bump seed, and a program's ID.
        # See: https://solana.com/docs/core/pda
        data = bytearray()
        data.extend(seed)
        data.append(0xff)
        data.extend(self.p)
        data.extend(bytearray('ProgramDerivedAddress'.encode()))
        for i in range(255, -1, -1):
            data[len(seed)] = i
            hash = bytearray(hashlib.sha256(data).digest())
            # The pda should fall off the ed25519 curve.
            if not pxsol.eddsa.pt_exists(hash):
                return PubKey(hash), i
        raise Exception

    def hex(self) -> str:
        # Convert the public key to hex representation.
        return self.p.hex()

    @classmethod
    def hex_decode(cls, data: str) -> PubKey:
        # Convert the hex representation to public key.
        return PubKey(bytearray.fromhex(data))

    def int(self) -> int:
        # Convert the public key to u256 number, in big endian.
        return int.from_bytes(self.p)

    @classmethod
    def int_decode(cls, data: int) -> PubKey:
        # Convert the u256 number to public key, in big endian.
        return PubKey(bytearray(data.to_bytes(32)))

    def json(self) -> str:
        return self.base58()


class AccountMeta:
    # Describes a single account with it's mode. The bit 0 distinguishes whether the account is writable; the bit 1
    # distinguishes whether the account needs to be signed. Details are as follows:
    #   0: readonly
    #   1: writable
    #   2: readonly + signer
    #   3: writable + signer

    def __init__(self, pubkey: PubKey, mode: int) -> None:
        self.pubkey = pubkey
        self.mode = mode

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> dict[str, str]:
        return {
            'pubkey': self.pubkey.base58(),
            'mode': ['-r', '-w', 'sr', 'sw'][self.mode],
        }


class AddressTableLookup:
    # Address table lookup describe an on-chain address lookup table to use for loading more readonly and writable
    # accounts in a single tx.

    def __init__(
        self,
        account_key: PubKey,
        writable_indexes: list[int],
        readonly_indexes: list[int],
    ) -> None:
        self.account_key = account_key  # Address lookup table account key.
        self.writable_indexes = writable_indexes  # List of indexes used to load writable account addresses.
        self.readonly_indexes = readonly_indexes  # List of indexes used to load readonly account addresses.

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> dict[str, typing.Any]:
        return {
            'account_key': self.account_key.base58(),
            'writable_indexes': self.writable_indexes,
            'readonly_indexes': self.readonly_indexes,
        }

    def serialize(self) -> bytearray:
        r = bytearray()
        r.extend(self.account_key.p)
        r.extend(pxsol.compact_u16.encode(len(self.writable_indexes)))
        r.extend(bytearray(self.writable_indexes))
        r.extend(pxsol.compact_u16.encode(len(self.readonly_indexes)))
        r.extend(bytearray(self.readonly_indexes))
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> AddressTableLookup:
        return AddressTableLookup.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> AddressTableLookup:
        account_key = PubKey(pxsol.io.read_full(reader, 32))
        writable_indexes = list(pxsol.io.read_full(reader, pxsol.compact_u16.decode_reader(reader)))
        readonly_indexes = list(pxsol.io.read_full(reader, pxsol.compact_u16.decode_reader(reader)))
        return AddressTableLookup(account_key, writable_indexes, readonly_indexes)


class Requisition:
    # A directive for a single invocation of a solana program.

    def __init__(self, program: PubKey, account: list[AccountMeta], data: bytearray) -> None:
        self.program = program
        self.account = account
        self.data = data

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> dict[str, typing.Any]:
        return {
            'program': self.program.base58(),
            'account': [e.json() for e in self.account],
            'data': pxsol.base58.encode(self.data),
        }


class Instruction:
    # A compact encoding of an instruction.

    def __init__(self, program: int, account: list[int], data: bytearray) -> None:
        # Identifies an on-chain program that will process the instruction. This is represented as an u8 index pointing
        # to an account address within the account addresses array.
        self.program = program
        # Array of u8 indexes pointing to the account addresses array for each account required by the instruction.
        self.account = account
        # A u8 byte array specific to the program invoked. This data specifies the instruction to invoke on the program
        # along with any additional data that the instruction requires (such as function arguments).
        self.data = data

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> dict[str, typing.Any]:
        return {
            'program': self.program,
            'account': self.account,
            'data': pxsol.base58.encode(self.data)
        }

    def serialize(self) -> bytearray:
        r = bytearray()
        r.append(self.program)
        r.extend(pxsol.compact_u16.encode(len(self.account)))
        for e in self.account:
            r.append(e)
        r.extend(pxsol.compact_u16.encode(len(self.data)))
        r.extend(self.data)
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> Instruction:
        return Instruction.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> Instruction:
        i = Instruction(0, [], bytearray())
        i.program = int(pxsol.io.read_full(reader, 1)[0])
        for _ in range(pxsol.compact_u16.decode_reader(reader)):
            i.account.append(int(pxsol.io.read_full(reader, 1)[0]))
        i.data = bytearray(pxsol.io.read_full(reader, pxsol.compact_u16.decode_reader(reader)))
        return i


class MessageHeader:
    # The message header specifies the privileges of accounts included in the transaction's account address array. It
    # is comprised of three bytes, each containing a u8 integer, which collectively specify:
    # 1. The number of required signatures for the transaction.
    # 2. The number of read-only account addresses that require signatures.
    # 3. The number of read-only account addresses that do not require signatures.

    def __init__(self, required_signatures: int, readonly_signatures: int, readonly: int) -> None:
        self.required_signatures = required_signatures
        self.readonly_signatures = readonly_signatures
        self.readonly = readonly

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> list:
        return [self.required_signatures, self.readonly_signatures, self.readonly]

    def serialize(self) -> bytearray:
        return bytearray([self.required_signatures, self.readonly_signatures, self.readonly])

    @classmethod
    def serialize_decode(cls, data: bytearray) -> MessageHeader:
        assert len(data) == 3
        return MessageHeader(data[0], data[1], data[2])

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> MessageHeader:
        return MessageHeader.serialize_decode(pxsol.io.read_full(reader, 3))


class Message:
    # A Solana transaction message (legacy). List of instructions to be processed atomically.

    def __init__(
        self,
        header: MessageHeader,
        account_keys: list[PubKey],
        recent_blockhash: bytearray,
        instructions: list[Instruction]
    ) -> None:
        self.header = header
        self.account_keys = account_keys
        self.recent_blockhash = recent_blockhash
        self.instructions = instructions

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> dict[str, typing.Any]:
        return {
            'header': self.header.json(),
            'account_keys': [e.base58() for e in self.account_keys],
            'recent_blockhash': pxsol.base58.encode(self.recent_blockhash),
            'instructions': [e.json() for e in self.instructions],
        }

    def serialize(self) -> bytearray:
        r = bytearray()
        r.extend(self.header.serialize())
        r.extend(pxsol.compact_u16.encode(len(self.account_keys)))
        for e in self.account_keys:
            r.extend(e.p)
        r.extend(self.recent_blockhash)
        r.extend(pxsol.compact_u16.encode(len(self.instructions)))
        for e in self.instructions:
            r.extend(e.serialize())
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> Message:
        return Message.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> Message:
        m = Message(MessageHeader.serialize_decode_reader(reader), [], bytearray(), [])
        for _ in range(pxsol.compact_u16.decode_reader(reader)):
            m.account_keys.append(PubKey(pxsol.io.read_full(reader, 32)))
        m.recent_blockhash = pxsol.io.read_full(reader, 32)
        for _ in range(pxsol.compact_u16.decode_reader(reader)):
            m.instructions.append(Instruction.serialize_decode_reader(reader))
        return m


class MessageV0:
    # A Solana transaction message (v0). This message format supports succinct account loading with on-chain address
    # lookup tables.

    def __init__(
        self,
        header: MessageHeader,
        account_keys: list[PubKey],
        recent_blockhash: bytearray,
        instructions: list[Instruction],
        address_table_lookups: list[AddressTableLookup],
    ) -> None:
        self.header = header
        self.account_keys = account_keys
        self.recent_blockhash = recent_blockhash
        self.instructions = instructions
        self.address_table_lookups = address_table_lookups

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def downgrade(self) -> Message:
        # Downgrade to a legacy message (without address table lookups).
        return Message(self.header, self.account_keys, self.recent_blockhash, self.instructions)

    def json(self) -> dict[str, typing.Any]:
        r = self.downgrade().json()
        r['address_table_lookups'] = [e.json() for e in self.address_table_lookups]
        return r

    def serialize(self) -> bytearray:
        r = bytearray([0x80])
        r.extend(self.downgrade().serialize())
        r.extend(pxsol.compact_u16.encode(len(self.address_table_lookups)))
        for e in self.address_table_lookups:
            r.extend(e.serialize())
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> MessageV0:
        return MessageV0.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> MessageV0:
        assert pxsol.io.read_full(reader, 1)[0] == 0x80
        m = Message.serialize_decode_reader(reader)
        m = MessageV0(m.header, m.account_keys, m.recent_blockhash, m.instructions, [])
        for _ in range(pxsol.compact_u16.decode_reader(reader)):
            m.address_table_lookups.append(AddressTableLookup.serialize_decode_reader(reader))
        return m


class Transaction:
    # An atomically-committed sequence of instructions (legacy).
    # See: https://github.com/anza-xyz/solana-sdk/blob/master/transaction/src/lib.rs
    # See: https://docs.rs/solana-transaction/latest/solana_transaction/struct.Transaction.html

    def __init__(self, signatures: list[bytearray], message: Message) -> None:
        self.signatures = signatures
        self.message = message

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> dict[str, typing.Any]:
        return {
            'signatures': [pxsol.base58.encode(e) for e in self.signatures],
            'message': self.message.json()
        }

    def requisition(self) -> list[Requisition]:
        # Convert the transaction to requisitions.
        m3 = self.message.header.required_signatures - self.message.header.readonly_signatures
        m2 = self.message.header.readonly_signatures
        m1 = len(self.message.account_keys) - self.message.header.required_signatures - self.message.header.readonly
        m0 = self.message.header.readonly
        m = [3] * m3 + [2] * m2 + [1] * m1 + [0] * m0
        r = []
        for i in self.message.instructions:
            program = (self.message.account_keys[i.program])
            account = [AccountMeta(self.message.account_keys[a], m[a]) for a in i.account]
            r.append(Requisition(program, account, i.data))
        return r

    @classmethod
    def requisition_decode(cls, pubkey: PubKey, data: list[Requisition]) -> Transaction:
        # Convert the requisitions to transaction. The given pubkey is the fee payer, means which one pays the
        # transaction. The fee payer is always writable and signer.
        account_flat: list[AccountMeta] = [AccountMeta(pubkey, 3)]
        for r in data:
            account_flat.append(AccountMeta(r.program, 0))
            account_flat.extend(r.account)
        account_list: list[AccountMeta] = []
        account_dict: dict[PubKey, int] = {}
        for a in account_flat:
            if a.pubkey not in account_dict:
                account_list.append(a)
                account_dict[a.pubkey] = len(account_list) - 1
                continue
            account_list[account_dict[a.pubkey]].mode |= a.mode
        account_list.sort(key=lambda x: x.mode, reverse=True)
        tx = Transaction([], Message(MessageHeader(0, 0, 0), [], bytearray(), []))
        tx.message.account_keys.extend([e.pubkey for e in account_list])
        tx.message.header.required_signatures = len([k for k in account_list if k.mode >= 2])
        tx.message.header.readonly_signatures = len([k for k in account_list if k.mode == 2])
        tx.message.header.readonly = len([k for k in account_list if k.mode == 0])
        for r in data:
            program = tx.message.account_keys.index(r.program)
            account = [tx.message.account_keys.index(a.pubkey) for a in r.account]
            tx.message.instructions.append(Instruction(program, account, r.data))
        return tx

    def serialize(self) -> bytearray:
        r = bytearray()
        r.extend(pxsol.compact_u16.encode(len(self.signatures)))
        for e in self.signatures:
            r.extend(e)
        r.extend(self.message.serialize())
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> Transaction:
        return Transaction.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> Transaction:
        s = []
        for _ in range(pxsol.compact_u16.decode_reader(reader)):
            s.append(pxsol.io.read_full(reader, 64))
        return Transaction(s, Message.serialize_decode_reader(reader))

    def sign(self, prikey: list[PriKey]) -> None:
        # Sign the transaction using the given private keys.
        assert self.message.header.required_signatures == len(prikey)
        demand = self.message.account_keys[:self.message.header.required_signatures]
        signer = {e.pubkey(): e for e in prikey}
        m = self.message.serialize()
        for e in demand:
            k = signer[e]
            self.signatures.append(k.sign(m))


class TransactionV0:
    # An atomically-committed sequence of instructions (v0).
    # See: https://github.com/anza-xyz/solana-sdk/blob/master/transaction/src/versioned/mod.rs

    def __init__(self, signatures: list[bytearray], message: MessageV0) -> None:
        self.signatures = signatures
        self.message = message

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> dict[str, typing.Any]:
        return {
            'signatures': [pxsol.base58.encode(e) for e in self.signatures],
            'message': self.message.json()
        }

    def serialize(self) -> bytearray:
        r = bytearray()
        r.extend(pxsol.compact_u16.encode(len(self.signatures)))
        for e in self.signatures:
            r.extend(e)
        r.extend(self.message.serialize())
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> TransactionV0:
        return TransactionV0.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> TransactionV0:
        s = []
        for _ in range(pxsol.compact_u16.decode_reader(reader)):
            s.append(pxsol.io.read_full(reader, 64))
        return TransactionV0(s, MessageV0.serialize_decode_reader(reader))

    def sign(self, prikey: list[PriKey]) -> None:
        # Sign the transaction using the given private keys.
        assert self.message.header.required_signatures == len(prikey)
        demand = self.message.account_keys[:self.message.header.required_signatures]
        signer = {e.pubkey(): e for e in prikey}
        m = self.message.serialize()
        for e in demand:
            k = signer[e]
            self.signatures.append(k.sign(m))


class TransactionClassify:
    # Classify the transaction version type.

    @classmethod
    def version(cls, data: bytearray) -> int:
        # Get the transaction version type.
        # - n <= 0x7f: transaction legacy
        # - n == 0x80: transaction v0
        return data[1 + data[0] * 64]


class TokenExtensionMetadataPointer:
    # Metadata pointer extension data for mints.

    def __init__(self, auth: PubKey, hold: PubKey) -> None:
        self.auth = auth  # Authority that can set the metadata address.
        self.hold = hold  # Account address that holds the metadata.

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> dict[str, str]:
        return {
            'auth': self.auth.base58(),
            'hold': self.hold.base58(),
        }

    def serialize(self) -> bytearray:
        return pxsol.borsh.Struct([
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
        ]).encode([self.auth.p, self.hold.p])

    @classmethod
    def serialize_decode(cls, data: bytearray) -> TokenExtensionMetadataPointer:
        return TokenExtensionMetadataPointer.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> TokenExtensionMetadataPointer:
        r = pxsol.borsh.Struct([
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
        ]).decode(reader)
        return TokenExtensionMetadataPointer(PubKey(bytearray(r[0])), PubKey(bytearray(r[1])))


class TokenExtensionMetadata:
    # Metadata pointer extension data for mints.
    # See: https://github.com/solana-program/token-metadata/tree/main/interface.

    def __init__(
        self,
        auth: PubKey,
        mint: PubKey,
        name: str,
        symbol: str,
        uri: str,
        addition: dict[str, str],
    ) -> None:
        self.auth = auth  # The authority that can sign to update the metadata.
        self.mint = mint  # The associated mint, used to counter spoofing to be sure that metadata belongs to.
        self.name = name  # The longer name of the token.
        self.symbol = symbol  # The shortened symbol for the token.
        self.uri = uri  # The uri pointing to richer metadata.
        self.addition = addition  # Any additional metadata about the token as key-value pairs.

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> dict[str, typing.Any]:
        return {
            'auth': self.auth.base58(),
            'mint': self.mint.base58(),
            'name': self.name,
            'symbol': self.symbol,
            'uri': self.uri,
            'addition': self.addition,
        }

    def serialize(self) -> bytearray:
        return pxsol.borsh.Struct([
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
            pxsol.borsh.String,
            pxsol.borsh.String,
            pxsol.borsh.String,
            pxsol.borsh.Dict([pxsol.borsh.String, pxsol.borsh.String]),
        ]).encode([self.auth.p, self.mint.p, self.name, self.symbol, self.uri, self.addition])

    @classmethod
    def serialize_decode(cls, data: bytearray) -> TokenExtensionMetadata:
        return TokenExtensionMetadata.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> TokenExtensionMetadata:
        r = pxsol.borsh.Struct([
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
            pxsol.borsh.String,
            pxsol.borsh.String,
            pxsol.borsh.String,
            pxsol.borsh.Dict([pxsol.borsh.String, pxsol.borsh.String]),
        ]).decode(reader)
        return TokenExtensionMetadata(PubKey(bytearray(r[0])), PubKey(bytearray(r[1])), r[2], r[3], r[4], r[5])


class TokenMint:
    # Account structure for storing token mint information.

    def __init__(
        self,
        auth_mint: PubKey | None,
        supply: int,
        decimals: int,
        inited: bool,
        auth_freeze: PubKey | None,
        extensions: dict[int, bytearray],
    ) -> None:
        self.auth_mint = auth_mint  # Optional authority used to mint new tokens.
        self.supply = supply  # Total supply of tokens.
        self.decimals = decimals  # Number of base 10 digits to the right of the decimal place.
        self.inited = inited  # Is true if this structure has been initialized.
        self.auth_freeze = auth_freeze  # Optional authority to freeze token accounts.
        self.extensions = extensions  # Extensions available to token mints and accounts.

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def extension_default_account_state(self) -> int:
        return self.extensions[0x06][0]

    def extension_metadata_pointer(self) -> TokenExtensionMetadataPointer:
        return TokenExtensionMetadataPointer.serialize_decode(self.extensions[0x12])

    def extension_metadata(self) -> TokenExtensionMetadata:
        return TokenExtensionMetadata.serialize_decode(self.extensions[0x13])

    def json(self) -> dict[str, typing.Any]:
        extensions = {}
        for k, v in self.extensions.items():
            # Decode known extensions.
            # https://docs.rs/spl-token-2022-interface/2.1.0/spl_token_2022_interface/extension/enum.ExtensionType.html
            match k:
                case 0x06: extensions['default_account_state'] = self.extension_default_account_state()
                case 0x12: extensions['metadata_pointer'] = self.extension_metadata_pointer().json()
                case 0x13: extensions['metadata'] = self.extension_metadata().json()
                case _: extensions[k] = v.hex()
        return {
            'auth_mint': self.auth_mint.base58() if self.auth_mint is not None else None,
            'supply': self.supply,
            'decimals': self.decimals,
            'inited': self.inited,
            'auth_freeze': self.auth_freeze.base58() if self.auth_freeze is not None else None,
            'extensions': extensions,
        }

    def serialize(self) -> bytearray:
        r = bytearray(82)
        if self.auth_mint is not None:
            r[0x00:0x04] = bytearray([0x01, 0x00, 0x00, 0x00])
            r[0x04:0x24] = self.auth_mint.p
        r[0x24:0x2c] = bytearray(self.supply.to_bytes(8, 'little'))
        r[0x2c] = self.decimals
        r[0x2d] = int(self.inited)
        if self.auth_freeze is not None:
            r[0x2e:0x32] = bytearray([0x01, 0x00, 0x00, 0x00])
            r[0x32:0x52] = self.auth_freeze.p
        if len(self.extensions) != 0:
            # Mint creators and account owners can opt-in to token-2022 features. Extension data is written after the
            # end of the account data in token, which is the byte at index 165. This means it is always possible to
            # differentiate mints and accounts.
            r.extend(bytearray(83))
            # Append account type mint.
            r.append(0x01)
            for k in sorted(list(self.extensions.keys())):
                v = self.extensions[k]
                r.extend(bytearray(k.to_bytes(2, 'little')))
                r.extend(bytearray(len(v).to_bytes(2, 'little')))
                r.extend(v)
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> TokenMint:
        auth_mint = None
        if data[0x00:0x04] == bytearray([0x01, 0x00, 0x00, 0x00]):
            auth_mint = PubKey(data[0x04:0x24])
        supply = int.from_bytes(data[0x24:0x2c], 'little')
        decimals = data[0x2c]
        inited = data[0x2d] != 0x00
        auth_freeze = None
        if data[0x2e:0x32] == bytearray([0x01, 0x00, 0x00, 0x00]):
            auth_freeze = PubKey(data[0x32:0x52])
        extensions = {}
        extensions_reader = io.BytesIO(data)
        extensions_reader.read(pxsol.program.Token.size_extensions_base)
        for _ in range(1 << 32):
            if extensions_reader.tell() >= len(data):
                break
            kype_byte = pxsol.io.read_full(extensions_reader, 2)
            kype = int.from_bytes(kype_byte, 'little')
            size_byte = pxsol.io.read_full(extensions_reader, 2)
            size = int.from_bytes(size_byte, 'little')
            body = pxsol.io.read_full(extensions_reader, size)
            extensions[kype] = body
        return TokenMint(auth_mint, supply, decimals, inited, auth_freeze, extensions)
