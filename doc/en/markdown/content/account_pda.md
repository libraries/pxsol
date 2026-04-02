# Solana/Account Model/Program Derived Addresses

When developing on Solana, you'll inevitably need to use Program Derived Addresses (PDAs). In simple terms, these are data account addresses exclusively controlled by your program. Unlike regular addresses, a PDA **has no private key**, no one can control it manually. Only your program can instruct it to perform actions.

## How PDAs Are Generated

A PDA is deterministically generated from a program's public key and a set of user-defined seeds (such as strings or wallet addresses). It's not randomly created, but rather predictably calculated in advance. Since it corresponds to no private key, no one including the program author can sign transactions on behalf of this address.

This is particularly important for decentralized applications (like on-chain wallets, order books, or voting systems), where the developer may need to assign a unique account to each user, but doesn't want users to be able to manage or tamper with the contents of that account themselves.

Recall the example from the previous section:

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
thb = pxsol.core.PubKey.base58_decode('F782pXBcfvHvb8eJfrDtyD7MBtQDfsrihSRjvzwuVoJU')
pda = thb.derive_pda(ada.pubkey.p)[0]
print(pda) # HCPe787nPq7TfjeFivP9ZvZwejTAq1PGGzch93qUYeC3
```

With just a few lines of code, we can generate a PDA, which is typically used as the user's data account under a specific program.

## How the Algorithm Works

Solana uses the ed25519 elliptic curve for its key pairs, where each account is identified by a 32-byte public key.

A PDA, however, is a deliberately constructed address that falls off the ed25519 curve. That means there is no valid private key for it, no one can perform standard signature operations. To make PDAs usable, the Solana runtime provides a special mechanism that allows programs to perform simulated signatures for their own derived addresses.

The PDA generation algorithm works as follows:

1. Concatenate the seed(s) with the program's public key.
2. Append a "bump" value, starting at 255 and counting down.
3. For each combination, hash the entire input.
4. Check whether the resulting address lies off the elliptic curve.
5. If so, it qualifies as a PDA and is returned.

Here's a full implementation in Python:

```py
class PubKey:
    # Solana's public key is a 32-byte array. The base58 representation of the public key is also referred to as the
    # address.

    def __init__(self, p: bytearray) -> None:
        assert len(p) == 32
        self.p = p

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
```

## Exercise

Q: What is the bump for?

A: The bump acts as a collision-avoidance mechanism. If a particular seed combination produces an invalid (on-curve) address, the algorithm tries different bump values until it finds a valid PDA.

Q: Can a PDA initiate transactions on its own?

A: No. PDAs have no private keys, so they cannot independently sign or initiate transactions. They can only be operated by the owning program.
