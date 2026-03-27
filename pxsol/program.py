import hashlib
import pxsol.bincode
import pxsol.borsh
import pxsol.core

# Solana programs mainly use two serialization formats, bincode and borsh. Their specifications can be found on the
# following web pages:
# Bincode: https://docs.rs/crate/bincode/2.0.1/source/docs/spec.md
# Borsh: https://github.com/near/borsh#specification


class AddressLookupTable:
    # See: https://solana.com/zh/developers/guides/advanced/lookup-tables
    # See: https://github.com/anza-xyz/solana-sdk/tree/master/address-lookup-table-interface

    pubkey = pxsol.core.PubKey.base58_decode('AddressLookupTab1e1111111111111111111111111')

    @classmethod
    def create_lookup_table(cls, slot: int, bump: int) -> bytearray:
        # Create an address lookup table. Account references:
        # 0. -w uninitialized address lookup table account.
        # 1. sr account used to derive and control the new address lookup table.
        # 2. sw account that will fund the new address lookup table.
        # 3. -r system program for cpi.
        return pxsol.bincode.Enum.encode(0) + pxsol.bincode.Struct([
            pxsol.bincode.U64,
            pxsol.bincode.U8,
        ]).encode([slot, bump])

    @classmethod
    def freeze_lookup_table(cls) -> bytearray:
        # Permanently freeze an address lookup table, making it immutable. Account references:
        # 0. -w address lookup table account to freeze.
        # 1. sr authority account used to derive and control the address lookup table.
        return pxsol.bincode.Enum.encode(1)

    @classmethod
    def extend_lookup_table(cls, pubkey: list[pxsol.core.PubKey]) -> bytearray:
        # Extend an address lookup table with new addresses. Account references:
        # 0. -w address lookup table account to extend.
        # 1. sr current authority.
        # 2. sw account that will fund the table reallocation.
        # 3. -r system program for cpi.
        return pxsol.bincode.Enum.encode(2) + pxsol.bincode.Struct([
            pxsol.bincode.Slice(pxsol.bincode.Array(pxsol.bincode.U8, 32))
        ]).encode([
            [e.p for e in pubkey]
        ])

    @classmethod
    def deactivate_lookup_table(cls) -> bytearray:
        # Deactivate an address lookup table, making it unusable and eligible for closure after a short period of time.
        # Account references:
        # 0. -w address lookup table account to deactivate.
        # 1. sr current authority.
        return pxsol.bincode.Enum.encode(3)

    @classmethod
    def close_lookup_table(cls) -> bytearray:
        # Close an address lookup table account. Account references:
        # 0. -w address lookup table account to close.
        # 1. sr current authority.
        # 2. -w recipient of closed account lamports.
        return pxsol.bincode.Enum.encode(4)


class AssociatedTokenAccount:
    # See: https://github.com/solana-program/associated-token-account

    pubkey = pxsol.core.PubKey.base58_decode('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL')

    @classmethod
    def create(cls) -> bytearray:
        # Creates an associated token account for the given wallet address and token mint. Returns an error if the
        # account exists. Account references:
        # 0. sw funding account (must be a system account).
        # 1. -w associated token account address to be created.
        # 2. -r wallet address for the new associated token account.
        # 3. -r the token mint for the new associated token account.
        # 4. -r system program.
        # 5. -r spl token program.
        return pxsol.borsh.Enum.encode(0)

    @classmethod
    def create_idempotent(cls) -> bytearray:
        # Creates an associated token account for the given wallet address and token mint, if it doesn't already exist.
        # Returns an error if the account exists, but with a different owner. Account references:
        # 0. sw funding account (must be a system account).
        # 1. -w associated token account address to be created.
        # 2. -r wallet address for the new associated token account.
        # 3. -r the token mint for the new associated token account.
        # 4. -r system program.
        # 5. -r spl token program.
        return pxsol.borsh.Enum.encode(1)

    @classmethod
    def recover_nested(cls) -> bytearray:
        # Transfers from and closes a nested associated token account: an associated token account owned by an
        # associated token account. The tokens are moved from the nested associated token account to the wallet's
        # associated token account, and the nested account lamports are moved to the wallet. Note: Nested token
        # accounts are an anti-pattern, and almost always created unintentionally, so this instruction should only be
        # used to recover from errors. Account references:
        # 0. -w nested associated token account, must be owned by 3.
        # 1. -r token mint for the nested associated token account.
        # 2. -w wallet's associated token account.
        # 3. -r owner associated token account address, must be owned by 5.
        # 4. -r token mint for the owner associated token account.
        # 5. sw wallet address for the owner associated token account.
        # 6. -r spl token program.
        return pxsol.borsh.Enum.encode(2)


class ComputeBudget:
    # See: https://github.com/anza-xyz/solana-sdk/tree/master/compute-budget-interface

    pubkey = pxsol.core.PubKey.base58_decode('ComputeBudget111111111111111111111111111111')

    @classmethod
    def request_heap_frame(cls, size: int) -> bytearray:
        # Request a specific transaction-wide program heap region size in bytes. The value requested must be a multiple
        # of 1024. This new heap region size applies to each program executed in the transaction, including all calls
        # to cpis.
        return pxsol.borsh.Enum.encode(1) + pxsol.borsh.U32.encode(size)

    @classmethod
    def set_compute_unit_limit(cls, size: int) -> bytearray:
        # Set a specific compute unit limit that the transaction is allowed to consume.
        return pxsol.borsh.Enum.encode(2) + pxsol.borsh.U32.encode(size)

    @classmethod
    def set_compute_unit_price(cls, unit: int) -> bytearray:
        # Set a compute unit price in "micro-lamports" to pay a higher transaction fee for higher transaction
        # prioritization. There are 10^6 micro-lamports in one lamport.
        assert unit <= 4  # Are you sure you want to pay such a high fee? You must have filled in the wrong number bro!
        return pxsol.borsh.Enum.encode(3) + pxsol.borsh.U64.encode(unit)

    @classmethod
    def set_loaded_accounts_data_size_limit(cls, size: int) -> bytearray:
        # Set a specific transaction-wide account data size limit, in bytes, is allowed to load.
        return pxsol.borsh.Enum.encode(4) + pxsol.borsh.U32.encode(size)


class LoaderV3:
    # The bpf loader program is the program that owns all executable accounts on solana. When you deploy a program, the
    # owner of the program account is set to the the bpf loader program. Loader v3 is also known as the upgradeable
    # loader.
    # See: https://github.com/anza-xyz/solana-sdk/blob/master/loader-v3-interface

    pubkey = pxsol.core.PubKey.base58_decode('BPFLoaderUpgradeab1e11111111111111111111111')

    # Account data is serialized by bincode. The enum type takes 4 bytes, and the option takes 1 byte.
    # Size of a buffer account's serialized metadata, calculated by the formula 4 + 1 + 32.
    size_program_buffer = 37
    # Size of a programdata account's serialized metadata, calculated by the formula 4 + 8 + 1 + 32.
    size_program_data = 45
    # Size of a serialized program account. calculated by the formula 4 + 32.
    size_program = 36

    @classmethod
    def initialize_buffer(cls) -> bytearray:
        # Initialize a Buffer account. Account references:
        # 0. -w source account to initialize.
        # 1. -r buffer authority. optional, if omitted then the buffer will be immutable.
        return pxsol.bincode.Enum.encode(0)

    @classmethod
    def write(cls, offset: int, data: bytearray) -> bytearray:
        # Write program data into a buffer account. Account references:
        # 0. -w buffer account to write program data to.
        # 1. sr buffer authority.
        return pxsol.bincode.Enum.encode(1) + pxsol.bincode.Struct([
            pxsol.bincode.U32,
            pxsol.bincode.Slice(pxsol.bincode.U8),
        ]).encode([offset, data])

    @classmethod
    def deploy_with_max_data_len(cls, size: int) -> bytearray:
        # Deploy an executable program. Account references:
        # 0. sw the payer account that will pay to create the program data account.
        # 1. -w the uninitialized program data account.
        # 2. -w The uninitialized program account.
        # 3. -w The buffer account where the program data has been written.
        # 4. -r rent sysvar.
        # 5. -r clock sysvar.
        # 6. -r system program.
        # 7. sr the program's authority.
        return pxsol.bincode.Enum.encode(2) + pxsol.bincode.U64.encode(size)

    @classmethod
    def upgrade(cls) -> bytearray:
        # Upgrade a program. Account references:
        # 0. -w the program data account.
        # 1. -w the program account.
        # 2. -w the buffer account where the program data has been written.
        # 3. -w the spill account.
        # 4. -r rent sysvar.
        # 5. -r clock sysvar.
        # 6. sr the program's authority.
        return pxsol.bincode.Enum.encode(3)

    @classmethod
    def set_authority(cls) -> bytearray:
        # Set a new authority that is allowed to write the buffer or upgrade the program. Account references:
        # 0. -w the buffer or program data account to change the authority of.
        # 1. sr the current authority.
        # 2. -r the new authority, optional, if omitted then the program will not be upgradeable.
        return pxsol.bincode.Enum.encode(4)

    @classmethod
    def close(cls) -> bytearray:
        # Closes an account owned by the upgradeable loader of all lamports and withdraws all the lamports.
        # 0. -w the account to close, if closing a program must be the program data account.
        # 1. -w the account to deposit the closed account's lamports.
        # 2. sr the account's authority, optional, required for initialized accounts.
        # 3. -w The associated program account if the account to close is a program data account.
        return pxsol.bincode.Enum.encode(5)

    @classmethod
    def extend_program(cls, size: int) -> bytearray:
        # Extend a program's program data account by the specified number of bytes. Only upgradeable program's can be
        # extended. Extend program was superseded by extend program checked. Account references:
        # 0. -w the program data account.
        # 1. -w the program data account's associated program account.
        # 2. -r system program, optional, used to transfer lamports from the payer to the program data account.
        # 3. sw The payer account, optional, that will pay necessary rent exemption costs for the increased storage.
        return pxsol.bincode.Enum.encode(6) + pxsol.bincode.U32.encode(size)

    @classmethod
    def set_authority_checked(cls) -> bytearray:
        # Set a new authority that is allowed to write the buffer or upgrade the program. This instruction differs from
        # set_authority in that the new authority is a required signer. Account references:
        # 0. -w the buffer or program data account to change the authority of.
        # 1. sr the current authority.
        # 2. sr the new authority, optional, if omitted then the program will not be upgradeable.
        return pxsol.bincode.Enum.encode(7)

    @classmethod
    def migrate(cls) -> bytearray:
        # Migrate the program to loader-v4. Account references:
        # 0. -w the program data account.
        # 1. -w the program account.
        # 2. sr the current authority.
        return pxsol.bincode.Enum.encode(8)

    @classmethod
    def extend_program_checked(cls, addi: int) -> bytearray:
        # Extend a program's program data account by the specified number of bytes. Only upgradeable programs can be
        # extended. Account references:
        # 0. -w the program data account.
        # 1. -w the program data account's associated program account.
        # 2. sr the authority.
        # 3. -r system program, optional, used to transfer lamports from the payer to the program data account.
        # 4. sr the payer account, optional, used to pay necessary rent exemption costs for the increased storage size.
        return pxsol.bincode.Enum.encode(9) + pxsol.bincode.U32.encode(addi)


LoaderUpgradeable = LoaderV3


class LoaderV4:
    # The v4 built-in loader program.
    # See: https://github.com/anza-xyz/solana-sdk/tree/master/loader-v4-interface

    pubkey = pxsol.core.PubKey.base58_decode('LoaderV411111111111111111111111111111111111')

    # Loader v4 account states size.
    size_program_data = 8 + 32 + 8

    @classmethod
    def write(cls, offset: int, data: bytearray) -> bytearray:
        # Write elf data into an undeployed program account. Account references:
        # 0. -w the program account to write to.
        # 1. sr the authority of the program.
        return pxsol.bincode.Enum.encode(0) + pxsol.bincode.Struct([
            pxsol.bincode.U32,
            pxsol.bincode.Slice(pxsol.bincode.U8),
        ]).encode([offset, data])

    @classmethod
    def copy(cls, dst_offset: int, src_offset: int, length: int) -> bytearray:
        # Copy elf data into an undeployed program account. Account references:
        # 0. -w the program account to write to.
        # 1. sr the authority of the program.
        # 2. -r the program account to copy from.
        return pxsol.bincode.Enum.encode(1) + pxsol.bincode.Struct([
            pxsol.bincode.U32,
            pxsol.bincode.U32,
            pxsol.bincode.U32,
        ]).encode([dst_offset, src_offset, length])

    @classmethod
    def set_program_length(cls, size: int) -> bytearray:
        # Changes the size of an undeployed program account. Account references:
        # 0. -w the program account to change the size of.
        # 1. sr the authority of the program.
        # 2. -w optional, the recipient account.
        return pxsol.bincode.Enum.encode(2) + pxsol.bincode.U32.encode(size)

    @classmethod
    def deploy(cls) -> bytearray:
        # Deploy a program account. Account references:
        # 0. -w the program account to deploy.
        # 1. sr the authority of the program.
        # 2. -w optional, an undeployed source program account to take data and lamports from.
        return pxsol.bincode.Enum.encode(3)

    @classmethod
    def retract(cls) -> bytearray:
        # Undo the deployment of a program account. Account references:
        # 0. -w the program account to retract.
        # 1. sr the authority of the program.
        return pxsol.bincode.Enum.encode(4)

    @classmethod
    def transfer_authority(cls) -> bytearray:
        # Transfers the authority over a program account. Account references:
        # 0. -w the program account to change the authority of.
        # 1. sr the current authority of the program.
        # 2. sr the new authority of the program.
        return pxsol.bincode.Enum.encode(5)

    @classmethod
    def finalize(cls) -> bytearray:
        # Finalizes the program account, rendering it immutable. Account references:
        # 0. -w the program account to change the authority of.
        # 1. sr the current authority of the program.
        # 2. -r the next version of the program (can be itself).
        return pxsol.bincode.Enum.encode(6)


class System:
    # The system program is responsible for the creation of accounts.
    # See: https://github.com/solana-program/system
    # See: https://github.com/anza-xyz/solana-sdk/blob/master/system-interface

    pubkey = pxsol.core.PubKey(bytearray(32))

    @classmethod
    def create_account(cls, lamports: int, size: int, host: pxsol.core.PubKey) -> bytearray:
        # Create a new account. Account references:
        # 0. sw funding account.
        # 1. sw new account.
        return pxsol.bincode.Enum.encode(0x00) + pxsol.bincode.Struct([
            pxsol.bincode.U64,
            pxsol.bincode.U64,
            pxsol.bincode.Array(pxsol.bincode.U8, 32),
        ]).encode([lamports, size, host.p])

    @classmethod
    def assign(cls, host: pxsol.core.PubKey) -> bytearray:
        # Assign account to a program. Account references:
        # 0. sw assigned account public key.
        return pxsol.bincode.Enum.encode(0x01) + pxsol.bincode.Array(pxsol.bincode.U8, 32).encode([e for e in host.p])

    @classmethod
    def transfer(cls, lamports: int) -> bytearray:
        # Transfer lamports. Account references:
        # 0. sw funding account.
        # 1. -w recipient account.
        return pxsol.bincode.Enum.encode(0x02) + pxsol.bincode.U64.encode(lamports)

    @classmethod
    def create_account_with_seed(
        cls,
        base: pxsol.core.PubKey,
        seed: bytearray,
        lamports: int,
        size: int,
        host: pxsol.core.PubKey,
    ) -> bytearray:
        # Create a new account at an address derived from a base pubkey and a seed. Account references:
        # 0. sw funding account.
        # 1. -w created account.
        # 2. sr base account.
        return pxsol.bincode.Enum.encode(0x03) + pxsol.bincode.Struct([
            pxsol.bincode.Array(pxsol.bincode.U8, 32),
            pxsol.bincode.Slice(pxsol.bincode.U8),
            pxsol.bincode.U64,
            pxsol.bincode.U64,
            pxsol.bincode.Array(pxsol.bincode.U8, 32),
        ]).encode([base.p, seed, lamports, size, host.p])

    @classmethod
    def advance_nonce_account(cls) -> bytearray:
        # Consumes a stored nonce, replacing it with a successor. Account references:
        # 0. -w nonce account.
        # 1. -r recent blockhashes sysvar.
        # 2. sr nonce authority.
        return pxsol.bincode.Enum.encode(0x04)

    @classmethod
    def withdraw_nonce_account(cls, lamports: int) -> bytearray:
        # Withdraw funds from a nonce account. Account references:
        # 0. -w nonce account.
        # 1. -w recipient account.
        # 2. -r recentBlockhashes sysvar.
        # 3. -r rent sysvar.
        # 4. sr nonce authority.
        return pxsol.bincode.Enum.encode(0x05) + pxsol.bincode.U64.encode(lamports)

    @classmethod
    def initialize_nonce_account(cls, host: pxsol.core.PubKey) -> bytearray:
        # Drive state of Uninitialized nonce account to Initialized, setting the nonce value. Account references:
        # 0. -w nonce account.
        # 1. -r recent blockhashes sysvar.
        # 2. -r rent sysvar.
        return pxsol.bincode.Enum.encode(0x06) + pxsol.bincode.Array(pxsol.bincode.U8, 32).encode([e for e in host.p])

    @classmethod
    def authorize_nonce_account(cls, host: pxsol.core.PubKey) -> bytearray:
        # Change the entity authorized to execute nonce instructions on the account. Account references:
        # 0. -w Nonce account
        # 1. sr Nonce authority
        return pxsol.bincode.Enum.encode(0x07) + pxsol.bincode.Array(pxsol.bincode.U8, 32).encode([e for e in host.p])

    @classmethod
    def allocate(cls, size: int) -> bytearray:
        # Allocate space in a (possibly new) account without funding. Account references:
        # 0. sw new account.
        return pxsol.bincode.Enum.encode(0x08) + pxsol.bincode.U64.encode(size)

    @classmethod
    def allocate_with_seed(
        cls,
        base: pxsol.core.PubKey,
        seed: bytearray,
        size: int,
        host: pxsol.core.PubKey,
    ) -> bytearray:
        # Allocate space for and assign an account at an address derived from a base public key and a seed.
        # Account references
        # 0. -w Allocated account
        # 1. sr Base account
        return pxsol.bincode.Enum.encode(0x09) + pxsol.bincode.Struct([
            pxsol.bincode.Array(pxsol.bincode.U8, 32),
            pxsol.bincode.Slice(pxsol.bincode.U8),
            pxsol.bincode.U64,
            pxsol.bincode.Array(pxsol.bincode.U8, 32),
        ]).encode([base.p, seed, size, host.p])

    @classmethod
    def assign_with_seed(cls, base: pxsol.core.PubKey, seed: bytearray, host: pxsol.core.PubKey) -> bytearray:
        # Assign account to a program based on a seed. Account references:
        # 0. -w Assigned account
        # 1. sr Base account
        return pxsol.bincode.Enum.encode(0x0a) + pxsol.bincode.Struct([
            pxsol.bincode.Array(pxsol.bincode.U8, 32),
            pxsol.bincode.Slice(pxsol.bincode.U8),
            pxsol.bincode.Array(pxsol.bincode.U8, 32),
        ]).encode([base.p, seed, host.p])

    @classmethod
    def transfer_with_seed(cls, lamports: int, seed: bytearray, host: pxsol.core.PubKey) -> bytearray:
        # Transfer lamports from a derived address. Account references:
        # 0. -w Funding account
        # 1. sr Base for funding account
        # 2. -w Recipient account
        return pxsol.bincode.Enum.encode(0x0b) + pxsol.bincode.Struct([
            pxsol.bincode.U64,
            pxsol.bincode.Slice(pxsol.bincode.U8),
            pxsol.bincode.Array(pxsol.bincode.U8, 32)
        ]).encode([lamports, seed, host.p])

    @classmethod
    def upgrade_nonce_account(cls) -> bytearray:
        # One-time idempotent upgrade of legacy nonce versions in order to bump them out of chain blockhash domain.
        # Account references:
        # 0. -w nonce account.
        return pxsol.bincode.Enum.encode(0x0c)

    @classmethod
    def create_account_allow_prefund(cls, lamports: int, size: int, host: pxsol.core.PubKey) -> bytearray:
        # Create a new account without enforcing the invariant that the account's current lamports must be 0. Account
        # references:
        # 0. sw new account.
        # 1. sw funding account. optional.
        return pxsol.bincode.Enum.encode(0x0d) + pxsol.bincode.Struct([
            pxsol.bincode.U64,
            pxsol.bincode.U64,
            pxsol.bincode.Array(pxsol.bincode.U8, 32),
        ]).encode([lamports, size, host.p])


class SysvarClock:
    # The Clock sysvar contains data on cluster time, including the current slot, epoch, and estimated wall-clock unix
    # timestamp. It is updated every slot.

    pubkey = pxsol.core.PubKey.base58_decode('SysvarC1ock11111111111111111111111111111111')


class SysvarRent:
    # The rent sysvar contains the rental rate. Currently, the rate is static and set in genesis. The rent burn
    # percentage is modified by manual feature activation.

    pubkey = pxsol.core.PubKey.base58_decode('SysvarRent111111111111111111111111111111111')


class Token:
    # Solana spl token.
    # See: https://github.com/solana-program/token-2022

    pubkey_2020 = pxsol.core.PubKey.base58_decode('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
    pubkey_2022 = pxsol.core.PubKey.base58_decode('TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb')
    pubkey = pubkey_2022
    # See: https://github.com/solana-labs/solana-program-library/blob/master/token/program-2022/src/state.rs
    size_mint = 82
    # The minimum for any account with extensions.
    size_extensions_base = 165 + 1
    # See: https://github.com/solana-program/token-2022/blob/main/interface/src/extension/default_account_state/mod.rs
    size_extensions_default_account_state = 4 + 1
    # See: https://github.com/solana-program/token-2022/blob/main/interface/src/extension/metadata_pointer/mod.rs
    size_extensions_metadata_pointer = 4 + 64
    # See: https://github.com/solana-program/token-metadata/blob/main/interface/src/state.rs
    size_extensions_metadata = 4 + 64 + 4 * 3 + 4

    @classmethod
    def initialize_mint(
        cls,
        decimals: int,
        auth_mint: pxsol.core.PubKey,
        auth_freeze: pxsol.core.PubKey | None,
    ) -> bytearray:
        # Initializes a new mint and optionally deposits all the newly minted tokens in an account. Account references:
        # 0. -w the mint to initialize.
        # 1. -r rent sysvar.
        return pxsol.borsh.Enum.encode(0x00) + pxsol.borsh.Struct([
            pxsol.borsh.U8,
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
            pxsol.borsh.Option(pxsol.borsh.Array(pxsol.borsh.U8, 32)),
        ]).encode([decimals, auth_mint.p, auth_freeze.p if auth_freeze is not None else None])

    @classmethod
    def initialize_account(cls) -> bytearray:
        # Initializes a new account to hold tokens. Account references:
        # 0. -w the account to initialize.
        # 1. -r the mint this account will be associated with.
        # 2. -r the new account's owner/multisignature.
        # 3. -r rent sysvar.
        return pxsol.borsh.Enum.encode(0x01)

    @classmethod
    def initialize_multisig(cls, m: int) -> bytearray:
        # Initializes a multisignature account with N provided signers. Account references:
        # 0. -w the multisignature account to initialize.
        # 1. -r rent sysvar
        # 2. -r the signer accounts, must equal to N where 1 <= N <= 11.
        return pxsol.borsh.Enum.encode(0x02) + pxsol.borsh.U8.encode(m)

    @classmethod
    def transfer(cls, amount: int) -> bytearray:
        # Transfers tokens from one account to another either directly or via a delegate. Account references:
        # 0. -w the source account.
        # 1. -w the destination account.
        # 2. sr the source account's owner/delegate.
        return pxsol.borsh.Enum.encode(0x03) + pxsol.borsh.U64.encode(amount)

    @classmethod
    def approve(cls, amount: int) -> bytearray:
        # Approves a delegate. A delegate is given the authority over tokens on behalf of the source account's owner.
        # Account references:
        # 0. -w the source account.
        # 1. -r the delegate.
        # 2. sr the source account owner.
        return pxsol.borsh.Enum.encode(0x04) + pxsol.borsh.U64.encode(amount)

    @classmethod
    def revoke(cls) -> bytearray:
        # Revokes the delegate's authority. Account references:
        # 0. -w the source account.
        # 1. sr the source account owner.
        return pxsol.borsh.Enum.encode(0x05)

    @classmethod
    def set_authority(cls, auth_type: int, auth: pxsol.core.PubKey | None) -> bytearray:
        # Sets a new authority of a mint or account. Argument auth_type is an enumeration value, please refer to the
        # rust source code. Account references:
        # 0. -w the mint or account to change the authority of.
        # 1. sr the current authority of the mint or account.
        return pxsol.borsh.Enum.encode(0x06) + pxsol.borsh.Struct([
            pxsol.borsh.Enum,
            pxsol.borsh.Option(pxsol.borsh.Array(pxsol.borsh.U8, 32)),
        ]).encode([auth_type, auth.p if auth is not None else None])

    @classmethod
    def mint_to(cls, amount: int) -> bytearray:
        # Mints new tokens to an account. Account references:
        # 0. -w the mint
        # 1. -w the account to mint tokens to.
        # 2. sr the mint's minting authority.
        return pxsol.borsh.Enum.encode(0x07) + pxsol.borsh.U64.encode(amount)

    @classmethod
    def burn(cls, amount: int) -> bytearray:
        # Burns tokens by removing them from an account. Account references:
        # 0. -w the account to burn from.
        # 1. -w the token mint.
        # 2. sr the account's owner/delegate.
        return pxsol.borsh.Enum.encode(0x08) + pxsol.borsh.U64.encode(amount)

    @classmethod
    def close_account(cls) -> bytearray:
        # Close an account by transferring all its sol to the destination account. Non-native accounts may only be
        # closed if its token amount is zero. Account references:
        # 0. -w the account to close.
        # 1. -w the destination account.
        # 2. sr the account's owner.
        return pxsol.borsh.Enum.encode(0x09)

    @classmethod
    def freeze_account(cls) -> bytearray:
        # Freeze an Initialized account using the Mint's freeze_authority (if set). Account references:
        # 0. -w the account to freeze.
        # 1. -r the token mint.
        # 2. sr the mint freeze authority.
        return pxsol.borsh.Enum.encode(0x0a)

    @classmethod
    def thaw_account(cls) -> bytearray:
        # Thaw a Frozen account using the Mint's freeze_authority (if set). Account references:
        # 0. -w the account to freeze
        # 1. -r the token mint
        # 2. sr the mint freeze authority.
        return pxsol.borsh.Enum.encode(0x0b)

    @classmethod
    def transfer_checked(cls, amount: int, decimals: int) -> bytearray:
        # Transfers tokens from one account to another either directly or via a delegate. Account references:
        # 0. -w the source account.
        # 1. -r the token mint.
        # 2. -w the destination account.
        # 3. sr the source account's owner/delegate.
        return pxsol.borsh.Enum.encode(0x0c) + pxsol.borsh.Struct([
            pxsol.borsh.U64,
            pxsol.borsh.U8,
        ]).encode([amount, decimals])

    @classmethod
    def approve_checked(cls, amount: int, decimals: int) -> bytearray:
        # Approves a delegate. Account references:
        # 0. -w the source account.
        # 1. -r the token mint.
        # 2. -r the delegate.
        # 3. sr the source account owner.
        return pxsol.borsh.Enum.encode(0x0d) + pxsol.borsh.Struct([
            pxsol.borsh.U64,
            pxsol.borsh.U8,
        ]).encode([amount, decimals])

    @classmethod
    def mint_to_checked(cls, amount: int, decimals: int) -> bytearray:
        # Mints new tokens to an account. Account references:
        # 0. -w the mint.
        # 1. -w the account to mint tokens to.
        # 2. sr the mint's minting authority.
        return pxsol.borsh.Enum.encode(0x0e) + pxsol.borsh.Struct([
            pxsol.borsh.U64,
            pxsol.borsh.U8,
        ]).encode([amount, decimals])

    @classmethod
    def burn_checked(cls, amount: int, decimals: int) -> bytearray:
        # Burns tokens by removing them from an account. Account references:
        # 0. -w the account to burn from.
        # 1. -w the token mint.
        # 2. sr the account's owner/delegate.
        return pxsol.borsh.Enum.encode(0x0f) + pxsol.borsh.Struct([
            pxsol.borsh.U64,
            pxsol.borsh.U8,
        ]).encode([amount, decimals])

    @classmethod
    def initialize_account2(cls, host: pxsol.core.PubKey) -> bytearray:
        # Like initialize_account(), but the owner pubkey is passed via instruction data rather than the accounts list.
        # Account references:
        # 0. -w the account to initialize.
        # 1. -r the mint this account will be associated with.
        # 2. -r rent sysvar
        return pxsol.borsh.Enum.encode(0x10) + pxsol.borsh.Array(pxsol.borsh.U8, 32).encode([e for e in host.p])

    @classmethod
    def sync_native(cls) -> bytearray:
        # Given a wrapped / native token account (a token account containing sol) updates its amount field based on the
        # account's underlying `lamports`. Account references:
        # 0. -w the native token account to sync with its underlying lamports.
        return pxsol.borsh.Enum.encode(0x11)

    @classmethod
    def initialize_account3(cls, host: pxsol.core.PubKey) -> bytearray:
        # Like initialize_account2(), but does not require the Rent sysvar to be provided. Account references:
        # 0. -w the account to initialize.
        # 1. -r the mint this account will be associated with.
        return pxsol.borsh.Enum.encode(0x12) + pxsol.borsh.Array(pxsol.borsh.U8, 32).encode([e for e in host.p])

    @classmethod
    def initialize_multisig2(cls, m: int) -> bytearray:
        # Like initialize_multisig(), but does not require the Rent sysvar to be provided. Account references:
        # 0. -w the multisignature account to initialize.
        # 1. -r the signer accounts, must equal to N where 1 <= N <= 11.
        return pxsol.borsh.Enum.encode(0x13) + pxsol.borsh.U8.encode(m)

    @classmethod
    def initialize_mint2(
        cls,
        decimals: int,
        auth_mint: pxsol.core.PubKey,
        auth_freeze: pxsol.core.PubKey | None,
    ) -> bytearray:
        # Like initialize_mint(), but does not require the Rent sysvar to be provided. Account references:
        # 0. -w the mint to initialize.
        return pxsol.borsh.Enum.encode(0x14) + pxsol.borsh.Struct([
            pxsol.borsh.U8,
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
            pxsol.borsh.Option(pxsol.borsh.Array(pxsol.borsh.U8, 32)),
        ]).encode([decimals, auth_mint.p, auth_freeze.p if auth_freeze is not None else None])

    @classmethod
    def get_account_data_size(cls, extension_type: list[int]) -> bytearray:
        # Gets the required size of an account for the given mint as a little-endian u64. Account references:
        # 0. -r the mint to calculate for.
        return pxsol.borsh.Enum.encode(0x15) + pxsol.borsh.Slice(pxsol.borsh.U16).encode(extension_type)

    @classmethod
    def initialize_immutable_owner(cls) -> bytearray:
        # Initialize the immutable owner extension for the given token account. Account references:
        # 0. -w the account to initialize.
        return pxsol.borsh.Enum.encode(0x16)

    @classmethod
    def amount_to_ui_amount(cls, amount: int) -> bytearray:
        # Convert an amount of tokens to a ui amount string, using the given mint. Account references:
        # 0. -r the mint to calculate for.
        return pxsol.borsh.Enum.encode(0x17) + pxsol.borsh.U64.encode(amount)

    @classmethod
    def ui_amount_to_amount(cls, amount: str) -> bytearray:
        # Convert a ui amount of tokens to a little-endian u64 raw amount, using the given mint. Account references:
        # 0. -r the mint to calculate for.
        return pxsol.borsh.Enum.encode(0x18) + pxsol.borsh.String.encode(amount)

    @classmethod
    def initialize_mint_close_authority(cls, close_authority: pxsol.core.PubKey | None) -> bytearray:
        # Initialize the close account authority on a new mint. Account references:
        # 0. -w the mint to initialize.
        return pxsol.borsh.Enum.encode(0x19) + pxsol.borsh.Struct([
            pxsol.borsh.Option(pxsol.borsh.Array(pxsol.borsh.U8, 32)),
        ]).encode([close_authority.p if close_authority is not None else None])

    @classmethod
    def transfer_fee_extension(cls) -> bytearray:
        # The common instruction prefix for transfer fee extension instructions.
        return pxsol.borsh.Enum.encode(0x1a)

    @classmethod
    def confidential_transfer_extension(cls) -> bytearray:
        # The common instruction prefix for confidential transfer extension instructions.
        return pxsol.borsh.Enum.encode(0x1b)

    @classmethod
    def default_account_state_extension(cls) -> bytearray:
        # The common instruction prefix for default account state extension instructions.
        return pxsol.borsh.Enum.encode(0x1c)

    @classmethod
    def reallocate(cls, extension_types: list[int]) -> bytearray:
        # Check to see if a token account is large enough for a list of extension types, and if not, use reallocation
        # to increase the data size. Account references:
        # 0. -w the account to reallocate.
        # 1. sw the payer account to fund reallocation
        # 2. -r system program for reallocation funding
        # 3. sr the account's owner.
        return pxsol.borsh.Enum.encode(0x1d) + pxsol.borsh.Slice(pxsol.borsh.U16).encode(extension_types)

    @classmethod
    def memo_transfer_extension(cls) -> bytearray:
        # The common instruction prefix for memo transfer account extension instructions.
        return pxsol.borsh.Enum.encode(0x1e)

    @classmethod
    def create_native_mint(cls) -> bytearray:
        # Creates the native mint. This instruction only needs to be invoked once after deployment and is
        # permissionless, Wrapped sOL will not be available until this instruction is successfully executed.
        # Account references:
        # 0. sw funding account (must be a system account)
        # 1. -w the native mint address
        # 2. -r system program for mint account funding
        return pxsol.borsh.Enum.encode(0x1f)

    @classmethod
    def initialize_non_transferable_mint(cls) -> bytearray:
        # Initialize the non transferable extension for the given mint account. Account references:
        # 0. -w The mint account to initialize.
        return pxsol.borsh.Enum.encode(0x20)

    @classmethod
    def interest_bearing_mint_extension(cls) -> bytearray:
        # The common instruction prefix for Interest Bearing extension instructions.
        return pxsol.borsh.Enum.encode(0x21)

    @classmethod
    def cpi_guard_extension(cls) -> bytearray:
        # The common instruction prefix for CPI Guard account extension instructions.
        return pxsol.borsh.Enum.encode(0x22)

    @classmethod
    def initialize_permanent_delegate(cls, delegate: pxsol.core.PubKey) -> bytearray:
        # Initialize the permanent delegate on a new mint. Account references:
        # 0. -w The mint to initialize.
        return pxsol.borsh.Enum.encode(0x23) + pxsol.borsh.Array(pxsol.borsh.U8, 32).encode([e for e in delegate.p])

    @classmethod
    def transfer_hook_extension(cls) -> bytearray:
        # The common instruction prefix for transfer hook extension instructions.
        return pxsol.borsh.Enum.encode(0x24)

    @classmethod
    def confidential_transfer_fee_extension(cls) -> bytearray:
        # The common instruction prefix for the confidential transfer fee extension instructions.
        return pxsol.borsh.Enum.encode(0x25)

    @classmethod
    def withdraw_excess_lamports(cls) -> bytearray:
        # This instruction is to be used to rescue sol sent to any token program owned account by sending them to any
        # other account, leaving behind only lamports for rent exemption. Account references:
        # 0. -w source account owned by the token program.
        # 1. -w destination account.
        # 2. sr authority.
        return pxsol.borsh.Enum.encode(0x26)

    @classmethod
    def metadata_pointer_extension(cls) -> bytearray:
        # The common instruction prefix for metadata pointer extension instructions.
        return pxsol.borsh.Enum.encode(0x27)

    @classmethod
    def group_pointer_extension(cls) -> bytearray:
        # The common instruction prefix for group pointer extension instructions.
        return pxsol.borsh.Enum.encode(0x28)

    @classmethod
    def group_member_pointer_extension(cls) -> bytearray:
        # The common instruction prefix for group member pointer extension instructions.
        return pxsol.borsh.Enum.encode(0x29)

    @classmethod
    def confidential_mint_burn_extension(cls) -> bytearray:
        # Instruction prefix for instructions to the confidential-mint-burn extension.
        return pxsol.borsh.Enum.encode(0x2a)

    @classmethod
    def scaled_ui_amount_extension(cls) -> bytearray:
        # Instruction prefix for instructions to the scaled ui amount extension.
        return pxsol.borsh.Enum.encode(0x2b)

    @classmethod
    def pausable_extension(cls) -> bytearray:
        # Instruction prefix for instructions to the pausable extension.
        return pxsol.borsh.Enum.encode(0x2c)

    @classmethod
    def unwrap_lamports(cls, amount: int | None) -> bytearray:
        # Transfer lamports from a native SOL account to a destination account. This is useful to unwrap lamports
        # from a wrapped SOL account. Account references:
        # 0. -w The source account.
        # 1. -w The destination account.
        # 2. sr The source account's owner/delegate.
        return pxsol.borsh.Enum.encode(0x2d) + pxsol.borsh.Option(pxsol.borsh.U64).encode(amount)


class TokenExtensionDefaultAccountState:
    # Solana spl token default account state extension.
    # See: https://github.com/solana-program/token-2022/tree/main/interface/src/extension/default_account_state
    # The account_state is an enumeration value: 0: uninitialized, 1: initialized, 2: frozen.

    @classmethod
    def initialize(cls, account_state: int) -> bytearray:
        # Initialize a new mint with the default state for new accounts. Account references:
        # 0. -w the mint to initialize.
        assert account_state in [0, 1, 2]
        return bytearray([0x1c, 0x00, account_state])

    @classmethod
    def update(cls, account_state: int) -> bytearray:
        # Update the default state for new accounts. Account references:
        # 0. -w the mint.
        # 1. sr the mint freeze authority.
        assert account_state in [0, 1, 2]
        return bytearray([0x1c, 0x01, account_state])


class TokenExtensionMetadataPointer:
    # Solana spl token metadata pointer extension.
    # See: https://github.com/solana-program/token-2022/tree/main/interface/src/extension/metadata_pointer

    @classmethod
    def initialize(cls, auth: pxsol.core.PubKey, mint: pxsol.core.PubKey) -> bytearray:
        # Initialize a new mint with a metadata pointer. Account references:
        # 0. -w the mint to initialize.
        return Token.metadata_pointer_extension() + pxsol.borsh.Enum.encode(0x00) + pxsol.borsh.Struct([
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
        ]).encode([auth.p, mint.p])

    @classmethod
    def update(cls, mint: pxsol.core.PubKey) -> bytearray:
        # Update the metadata pointer address. Only supported for mints that include the metadata pointer extension.
        # Account references:
        # 0. -w the mint.
        # 1. sr the metadata pointer authority.
        return Token.metadata_pointer_extension() + pxsol.borsh.Enum.encode(0x01) + pxsol.borsh.Struct([
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
        ]).encode([mint.p])


class TokenExtensionMetadata:
    # Solana spl token metadata.
    # See: https://github.com/solana-program/token-metadata

    @classmethod
    def initialize(cls, name: str, symbol: str, uri: str) -> bytearray:
        # Initializes a tlv entry with the basic token-metadata fields. Account references:
        # 0. -w metadata.
        # 1. -r update authority.
        # 2. -r mint.
        # 3. sr mint authority.
        discriminator = bytearray(hashlib.sha256(b'spl_token_metadata_interface:initialize_account').digest()[:8])
        return pxsol.borsh.Struct([
            pxsol.borsh.Array(pxsol.borsh.U8, 8),
            pxsol.borsh.String,
            pxsol.borsh.String,
            pxsol.borsh.String,
        ]).encode([discriminator, name, symbol, uri])

    @classmethod
    def update_field(cls, field: str, value: str) -> bytearray:
        # Updates a field in a token-metadata account. The field can be one of the required fields (name, symbol, uri),
        # or a totally new field denoted by a "key" string. Account references:
        # 0. -w metadata account.
        # 1. sr update authority.
        discriminator = bytearray(hashlib.sha256(b'spl_token_metadata_interface:updating_field').digest()[:8])
        defaultfields = ['name', 'symbol', 'uri']
        match field:
            case 'name' | 'symbol' | 'uri':
                enum = defaultfields.index(field)
                return pxsol.borsh.Struct([
                    pxsol.borsh.Array(pxsol.borsh.U8, 8),
                    pxsol.borsh.Enum,
                    pxsol.borsh.String,
                ]).encode([discriminator, enum, value])
            case _:
                return pxsol.borsh.Struct([
                    pxsol.borsh.Array(pxsol.borsh.U8, 8),
                    pxsol.borsh.Enum,
                    pxsol.borsh.String,
                    pxsol.borsh.String,
                ]).encode([discriminator, 0x03, field, value])

    @classmethod
    def remove_key(cls, idempotent: bool, key: str) -> bytearray:
        # Removes a key-value pair in a token-metadata account. This only applies to additional fields, and not the
        # base name / symbol / uri fields. Account references:
        # 0. -w metadata account.
        # 1. sr update authority.
        discriminator = bytearray(hashlib.sha256(b'spl_token_metadata_interface:remove_key_ix').digest()[:8])
        return pxsol.borsh.Struct([
            pxsol.borsh.Array(pxsol.borsh.U8, 8),
            pxsol.borsh.Bool,
            pxsol.borsh.String,
        ]).encode([discriminator, idempotent, key])

    @classmethod
    def update_authority(cls, auth: pxsol.core.PubKey | None) -> bytearray:
        # Updates the token-metadata authority. Account references:
        # 0. -w metadata account.
        # 1. sr current update authority.
        discriminator = bytearray(hashlib.sha256(b'spl_token_metadata_interface:update_the_authority').digest()[:8])
        return pxsol.borsh.Struct([
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
        ]).encode([discriminator, auth.p if auth is not None else None])

    @classmethod
    def emit(cls, start: int | None, end: int | None) -> bytearray:
        # Emits the token-metadata as return data. Account references:
        # 0. -r metadata account.
        discriminator = bytearray(hashlib.sha256(b'spl_token_metadata_interface:emitter').digest()[:8])
        return pxsol.borsh.Struct([
            pxsol.borsh.Array(pxsol.borsh.U8, 32),
            pxsol.borsh.Option(pxsol.borsh.U64),
            pxsol.borsh.Option(pxsol.borsh.U64),
        ]).encode([discriminator, start, end])
