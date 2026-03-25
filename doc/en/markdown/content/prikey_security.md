# Solana/Private Key, Public Key and Address/How to Securely Protect Your Private Key

Private keys are the most critical asset credentials in the blockchain world. The phrase "not your keys, not your coins" perfectly captures their importance. Once a private key is leaked or lost, your digital assets will be permanently lost or stolen.

I'll briefly discuss private key security protection here, including warnings from real-world cases, understanding from a cryptographic perspective, and practical security measures.

## Case Studies and Warnings

### Trust Wallet Supply Chain Attack

This is a case that occurred at the end of 2025, and it's the first one that came to my mind.

On December 25, 2025, community security analyst akinator issued an alert warning that the Trust Wallet browser extension may have suffered a supply chain attack, advising users not to import seed phrases or use the extension. The tweet claimed over $2 million had been stolen, with attackers using multiple addresses for fund transfers.

<https://x.com/0xakinator/status/2004273944694587785>

The tweet pointed to December 24, 2025, when Trust Wallet Chrome extension v2.68 update was released, but this version was injected with malicious code, causing user information to be stolen and sent to attackers when importing seed phrases.

By December 27, 2025, losses had escalated to $7 million. The official team subsequently released a statement, acknowledging the extension was compromised and advising users to immediately stop using it. At this point, three days had passed since the attack, but losses continued to increase.

What's most shocking about this attack is that victims didn't click phishing links or download fake apps—they used an extension updated through official channels. In other words, the infrastructure we thought was secure.

**Today, most systems rely on complete access to user information: viewing all data, storing everything, and then having users pray that nothing goes wrong.**

> Question: Is storing private keys in wallets truly secure? While this was an attack incident, it also exposed that users have no defense if the wallet provider decides to act maliciously. This is why I've always believed that private key security is not just a technical issue, but a trust issue.

### Clipboard Attacks

Some malware monitors clipboard content, and when detecting strings resembling private keys or seed phrases, sends the data to remote servers. Even some legitimate software often logs clipboard content to files or sends it to remote servers, which can also lead to private key leaks.

There are numerous reports of such attacks, with similar warnings appearing in the blockchain community at regular intervals.

### New Threat: Coding Agents

A new type of attack is currently gaining popularity online: exploiting AI code generation tools (such as GitHub Copilot, Claude, etc.) to steal users' source code, which may very well contain your private keys.

The root of the problem is similar to the examples above: coding agents have complete access to your code repository, can view and modify all files, while allowing AI to access the network or send data to it. If you use purchased AI services, all contents of your code repository are uploaded to the cloud for processing and storage. In August 2025, GitHub Copilot experienced a data leak where the AI mistakenly exposed responses intended for user A to user B. The root cause was a bug in Google Cloud Platform's proxy infrastructure that caused incorrect routing during request processing. While this incident didn't directly lead to private key leaks, it exposed the potential risks of AI services handling user data: the AI service provider you pay for can see all your code, including sensitive information.

Related disclosure: <https://docs.cloud.google.com/support/bulletins#gcp-2025-059>.

Even using locally deployed AI isn't completely safe. Suppose you clone a project from GitHub that happens to include files meant for AI to read, containing prompts that might instruct the AI to call curl to upload local files to a specified server. When you open that project in your editor, your locally configured AI might automatically execute that command. This vulnerability exploits human trust in AI, and there are currently no effective protective measures.

## Private Key Security from a Cryptographic Perspective

### Private Key Generation

A private key is essentially a random large integer. Taking Solana's ed25519 as an example, a private key is a 256-bit random number ranging from 0 to 2^256 - 1. How large is this number? The number of observable atoms in the universe is approximately 10^80. Brute-forcing a private key is computationally infeasible.

During private key generation, a high-quality random number generator must be used to ensure unpredictability. We typically use hardware entropy sources (such as `/dev/random`). Simultaneously ensure the security of the generation environment to prevent malware from stealing entropy source data.

If you're just storing a small amount of money, using official wallets to generate private keys is generally secure enough. But if you hold large amounts of assets, stricter measures are needed. I only recommend one approach: flip a coin 256 times, record heads or tails on an offline computer, then convert the results into a 256-bit number—this is your private key.

> There was once an attack incident where a well-known wallet application used a low-quality random number generator when generating private keys. Attackers could guess all private keys generated within a certain time period.

> There was once an attack incident where a well-known wallet application deliberately planted malicious code, sending private key results to remote servers during generation.

### Private Key Storage

**Software Wallets**

Current mainstream cryptographic schemes in use are secure enough to resist brute-force attacks (considering current technology levels). The real threat to private keys isn't cracking, but improper storage.

Modern wallets typically use password encryption to store private keys, with encryption schemes usually choosing AES or ChaCha20, then using key derivation algorithms: PBKDF2, Argon2, scrypt, etc. Typical encryption process:

1. User sets a password.
2. Use KDF (Key Derivation Function) to convert password into encryption key.
3. Use encryption key to encrypt private key.
4. Store encrypted key file.

However, this approach also carries risks, as the strength of the user's password becomes the weak link in the entire chain.

1. Weak passwords can theoretically be easily brute-forced; for example, common passwords like `123456`, `qwerty` can be cracked in seconds, leading to private key leaks. Therefore, you must choose a strong password. Additionally, even encrypted private key files shouldn't be stored on internet-connected devices, as attackers might obtain this encrypted file through other vulnerabilities and perform offline brute-force attacks. This is why I don't recommend using software wallets to store large amounts of assets. The security of software wallets largely depends on user password strength and device security, both of which are difficult to guarantee.
2. However, the computational cost of KDF makes brute-force attacks more difficult. The core of the algorithm is to increase the computational cost of password attempts, for example, by performing millions of hash iterations on the input password, making each password attempt take considerable time.

**Paper Wallets**

![img](../img/prikey_security/paper_wallet.jpg)

A once-popular physical cold storage solution whose security depends on the physical security of paper. The advantage of paper wallets is being completely offline, immune to network attacks. But they also have some drawbacks:

- Paper may be lost due to fire, loss, or physical damage.
- Requires printing the private key on paper. Depending on printer security, there may be leakage risks. Some printers store printed documents internally or send data to manufacturers' servers via network.

Therefore, the following alternative solution is now more commonly used.

**Metal Wallets**

![img](../img/prikey_security/metal_wallet.jpg)

Simply put, it solves all physical security issues of paper wallets and is currently the most recommended physical cold storage solution.

**Off-chain Multisig (Naive Version)**

A classic counterexample in the cryptographic community: simply splitting a private key string into several parts and storing them separately. For example, splitting a 64-character hexadecimal private key into 4 segments of 16 characters each, storing them in different physical locations (like home safe, bank safety deposit box, with friends, etc.). Assuming you want to protect private key e, you might split it like this:

```py
e = "1ec580e8913d9d2874bde4585eba9ae9aca20b80e40c114ec0b230dc4431bd71"

a = "1ec580e8913d9d28"
b = "74bde4585eba9ae9"
c = "aca20b80e40c114e"
d = "c0b230dc4431bd71"
assert a + b + c + d == e
```

This method is widely regarded as the most insecure practice because it cannot provide true threshold protection. Threshold protection means that only when a certain number of shares are combined can the complete private key be recovered. With this simple splitting method, as long as any one share is leaked, it's enough for attackers to obtain partial information and attempt all possible combinations through exhaustive methods to recover the private key. For example, if an attacker obtains a and b, they only need to try all possible combinations of c and d to recover the complete private key. At this point, the attacker only needs to try 2^128 combinations, far less than the 2^256 combinations needed to brute-force the entire private key.

Core problem: Partial shares leak partial information about the private key.

**Off-chain Multisig (Elder Version)**

A method in the cryptographic community that's not recommended but relatively secure and simple. The approach is still splitting, but instead of simple concatenation, it uses addition operations for protection. Treat the private key you want to protect as a large integer, then randomly generate a batch of large integers such that all randomly generated large integers sum modulo a large prime number equals the original private key. This way, only when attackers obtain all shares can they recover the complete private key. For example, with private key c, you can split it like this:

```py
import pabtc

c = 0xf108bf1b32f3eb50da02419afe6caee4f8385fe7df364f8af27e05757ba2ad04

a = 0x01d487c418d34e79760f835f8fb7309d3b0c6a0ab32f7bca2eebb7090bb1e9d3
b = 0xef3437571a209cd763f2be3b6eb57e47bd2bf5dd2c06d3c0c3924e6c6ff0c331
assert (a + b) % pabtc.secp256k1.N == c
```

This method, even if one share (a or b) is leaked, cannot leak any information about the complete private key c, because attackers cannot infer c's value from only a or b. However, the downside of this method is that all shares must be kept safe; if any share is lost, the complete private key cannot be recovered.

**Off-chain Threshold Signatures (Shamir's Secret Sharing)**

A scheme widely discussed in the Bitcoin community and personally recommended by me. This scheme is based on Shamir's Secret Sharing (SSS) algorithm, allowing private keys to be split into n shares with a threshold k set, where only when at least k shares are combined can the complete private key be recovered. This way, even if attackers obtain fewer than k shares, they cannot recover the complete private key. Its advantage is avoiding single points of failure: even if a share is lost, as long as the remaining number of shares reaches threshold k, the complete private key can still be recovered.

Common splitting methods are 2-of-3, 3-of-5, etc. For example, in a 3-of-5 scheme, the private key is split into 5 shares, and any 3 shares combined can recover the complete private key.

Related reading: <https://en.wikipedia.org/wiki/Shamir%27s_secret_sharing>

Brief introduction to algorithm principles:

0. k points on a plane can uniquely determine a k-1 degree curve. Treat the private key secret as a point at `(0, secret)`, then randomly generate `k - 1` random points to determine a curve on the plane.
1. Randomly select n points on the curve excluding `(0, secret)`, and save the coordinates of these points as shares.
2. When recovering the private key, simply substitute the coordinates of any k shares into Lagrange interpolation formula to recover the original polynomial, then substitute x=0 to obtain the private key secret. This is a simple k-of-n threshold scheme.

Advantages:

- The algorithm is open source with extensive application and research support. You don't need to rely on specific software or third-party libraries to implement the algorithm; any skilled programmer can implement code based on the publicly available algorithm.
- Even if all shares are leaked, attackers may not necessarily know you're using the SSS algorithm to protect private keys. They might think these shares are multiple private keys, which can increase the attacker's guessing difficulty. You can even actually use shares as private keys, storing small amounts of funds in them to create a honeypot deception layer. Attackers might be attracted to these small amounts and overlook the real private key. Once attackers transfer funds from the shares, you get an early warning: one of your shares has been leaked.

You can find an SSS algorithm implementation for Bitcoin private keys in my pabtc library: <https://github.com/libraries/pabtc/blob/master/example/sss.py>.

**Summary**

Two principles:

1. The plaintext of private keys should never appear on internet-connected devices. You should write them on paper or engrave them on metal plates.
2. Use some method to split private keys into multiple parts and store these parts according to the first principle.

## Quantum Attacks

The emergence of quantum computers poses a threat to existing public-key cryptography. Famous algorithms like Shor's algorithm can break encryption algorithms based on integer factorization and discrete logarithm problems in polynomial time. ECDSA used by Bitcoin and Ethereum, and ed25519 used by Solana, are all based on discrete logarithm problems, falling squarely within Shor's algorithm's attack range.

The Bitcoin community has begun discussing the adoption of quantum-resistant signature algorithms, but there's currently no widely supported solution. Potential alternatives include algorithms like SPHINCS and Falcon. For Bitcoin users, the current best practice is to create a new address to receive funds and never use this address to sign any transactions. This way, even if quantum computers emerge, they cannot crack this address's private key. The principle behind this is that for Bitcoin, signing transactions exposes the public key, and quantum computers can use the public key to crack the private key. As long as transactions aren't signed, the public key won't be exposed, and thus the private key won't be cracked.

> When Satoshi Nakamoto designed Bitcoin, he likely didn't know that elliptic curve public keys could be compressed. He thought public keys were too long, so he designed an address system that hashes the public key to generate a shorter address. This design was intended to save space at the time, but in hindsight, it also inadvertently provided an additional layer of security protection, because hash algorithms are quantum-resistant. Even if quantum computers emerge, they cannot reverse-engineer the original from hash values, thus protecting Bitcoin users' public keys from exposure and protecting private key security.

For Solana users, there's currently no clear quantum-resistant solution, nor can they adopt Bitcoin's approach, because Solana addresses are the public keys themselves. Therefore, Solana users need to more closely monitor quantum computing developments.

Practical quantum computers may still need several years, with Google researchers saying 5 to 10 years. We must face the threat of quantum computers now. It's not something that will only happen in the distant future.
