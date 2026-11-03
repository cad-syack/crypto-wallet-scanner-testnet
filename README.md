# Crypto Wallet Scanner — Testnet Lab

A Windows-friendly Python/Tkinter GUI that generates a fresh local BIP-39 12-word mnemonic, derives public addresses, and checks **testnet-only** balances on:
- Bitcoin Testnet (tBTC)
- Ethereum Sepolia (test ETH)
- BNB Smart Chain Testnet (test BNB)

This is a learning and development tool. It does not brute-force third-party wallets, search for real funded wallets, or support mainnet balance scanning.

## Requirements
- Windows 10 or 11
- Python 3.10 or newer from https://www.python.org/downloads/
- During Python installation, enable **Add python.exe to PATH**
- Internet connection for testnet balance lookups

## Setup
1. Extract the ZIP to a folder, for example `C:\CryptoWalletScanner`.
2. Open that folder in File Explorer.
3. Click the address bar, type `cmd`, and press Enter.
4. Run:

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python app.py
   ```

Or double-click `run_windows.bat` after dependencies are installed.

## How to use
1. Click **Generate test wallet**.
2. Click **Check testnet balances** to query public testnet endpoints.
3. Use **Show recovery phrase** only when needed. The phrase is kept in the app's memory and is not intentionally written to a file or sent to an RPC endpoint.
4. **Clear local secrets** removes the phrase from the app's active state. Python cannot guarantee secure memory erasure.
5. Double-click an address row or select it and click **Copy selected address** to copy the public address.

New wallets usually have zero balance. Testnet coins have no intended monetary value. Obtain test coins only from reputable testnet faucets, and never send real cryptocurrency to these addresses.

## Networks and derivation
- BTC Testnet: BIP-44 testnet coin configuration via `bip-utils`.
- Ethereum Sepolia: Ethereum BIP-44 address derivation.
- BNB Smart Chain Testnet: uses the same EVM address derived for Ethereum; the same private key corresponds to the same EVM address across EVM-compatible networks.

The app checks native coin balances only. It does not currently enumerate ERC-20/BEP-20 tokens or Bitcoin UTXO details.

## Endpoints
Default read-only endpoints:
- Bitcoin Testnet: `https://mempool.space/testnet/api`
- Ethereum Sepolia RPC: `https://ethereum-sepolia-rpc.publicnode.com`
- BNB Smart Chain Testnet RPC: `https://bsc-testnet-rpc.publicnode.com`

Public endpoints can be unavailable, rate-limited, or change their policies. For reliability, replace them with endpoints from providers you trust. Requests send public addresses only, never the mnemonic.

## Security notes
- **Never enter a mainnet seed phrase into this app.**
- Do not reuse testnet mnemonics for real wallets.
- Do not share screenshots that reveal a recovery phrase.
- Clipboard contents can be read by other applications; avoid copying phrases unless necessary.
- The app does not save the phrase to disk, but a local computer with malware or an administrator-level attacker may still expose process memory or clipboard contents.
- Dependencies are third-party packages. Install only from trusted package indexes and keep Python and dependencies updated.
- No executable is included; this ZIP contains source code. Review the code before running it.
