import threading
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
import requests

APP_TITLE = "Crypto Wallet Scanner — Testnet Lab"
TIMEOUT = 12

# Public read-only testnet endpoints. You can change these to your own RPC endpoints.
ETH_SEPOLIA_RPC = "https://ethereum-sepolia-rpc.publicnode.com"
BSC_TESTNET_RPC = "https://bsc-testnet-rpc.publicnode.com"
BTC_TESTNET_API = "https://mempool.space/testnet/api"

class WalletScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("900x690")
        self.root.minsize(760, 600)
        self.mnemonic = None
        self.wallet_data = {}
        self._style()
        self._build()

    def _style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 10))
        style.configure("Card.TLabelframe", padding=12)
        style.configure("Card.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)

    def _build(self):
        outer = ttk.Frame(self.root, padding=18)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Crypto Wallet Scanner", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="TESTNET ONLY • Generates local test wallets and checks public testnet balances",
            style="Sub.TLabel"
        ).pack(anchor="w", pady=(3, 14))

        warning = ttk.Label(
            outer,
            text="Safety: this app is configured for Bitcoin testnet, Ethereum Sepolia, and BNB Smart Chain testnet. "
                 "Never enter a mainnet seed phrase. Never fund a wallet using real cryptocurrency.",
            wraplength=830,
            justify="left"
        )
        warning.pack(fill="x", pady=(0, 12))

        actions = ttk.LabelFrame(outer, text="1. Create a test wallet", style="Card.TLabelframe")
        actions.pack(fill="x", pady=(0, 12))
        row = ttk.Frame(actions)
        row.pack(fill="x")
        ttk.Button(row, text="Generate test wallet", style="Accent.TButton",
                   command=self.generate_wallet).pack(side="left")
        ttk.Button(row, text="Show recovery phrase", command=self.show_phrase).pack(side="left", padx=8)
        ttk.Button(row, text="Clear local secrets", command=self.clear_secrets).pack(side="left")

        self.status_var = tk.StringVar(value="Ready. Generate a test wallet to begin.")
        ttk.Label(actions, textvariable=self.status_var, wraplength=800).pack(anchor="w", pady=(10, 0))

        wallets = ttk.LabelFrame(outer, text="2. Derived testnet addresses", style="Card.TLabelframe")
        wallets.pack(fill="both", expand=True, pady=(0, 12))
        self.tree = ttk.Treeview(wallets, columns=("network", "address", "balance"), show="headings", height=7)
        self.tree.heading("network", text="Network")
        self.tree.heading("address", text="Testnet address")
        self.tree.heading("balance", text="Balance")
        self.tree.column("network", width=170, anchor="w")
        self.tree.column("address", width=470, anchor="w")
        self.tree.column("balance", width=150, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.copy_selected_address)

        bottom = ttk.Frame(wallets)
        bottom.pack(fill="x", pady=(8, 0))
        ttk.Button(bottom, text="Check testnet balances", style="Accent.TButton",
                   command=self.check_balances).pack(side="left")
        ttk.Button(bottom, text="Copy selected address", command=self.copy_selected_address).pack(side="left", padx=8)

        logframe = ttk.LabelFrame(outer, text="Activity log", style="Card.TLabelframe")
        logframe.pack(fill="x")
        self.log = tk.Text(logframe, height=5, wrap="word", state="disabled", font=("Consolas", 9))
        self.log.pack(fill="x")

        self._log("App started. No wallet secrets have been loaded or transmitted.")

    def _log(self, message):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def generate_wallet(self):
        try:
            from bip_utils import (
                Bip39MnemonicGenerator, Bip39WordsNum, Bip39SeedGenerator,
                Bip44, Bip44Coins, Bip44Changes
            )
            mnemonic = str(Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12))
            seed = Bip39SeedGenerator(mnemonic).Generate()

            btc_ctx = Bip44.FromSeed(seed, Bip44Coins.BITCOIN_TESTNET).Purpose().Coin().Account(0).Change(
                Bip44Changes.CHAIN_EXT).AddressIndex(0)
            eth_ctx = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM).Purpose().Coin().Account(0).Change(
                Bip44Changes.CHAIN_EXT).AddressIndex(0)

            btc_address = btc_ctx.PublicKey().ToAddress()
            eth_address = eth_ctx.PublicKey().ToAddress()

            self.mnemonic = mnemonic
            self.wallet_data = {
                "BTC Testnet": btc_address,
                "Ethereum Sepolia": eth_address,
                "BNB Smart Chain Testnet": eth_address,
            }
            for item in self.tree.get_children():
                self.tree.delete(item)
            for network, address in self.wallet_data.items():
                self.tree.insert("", "end", values=(network, address, "Not checked"))
            self.status_var.set("Test wallet generated locally. Keep the recovery phrase private; this app will not save it to disk.")
            self._log("Generated a fresh 12-word testnet mnemonic locally. Addresses derived for BTC testnet, Sepolia, and BNB testnet.")
        except ImportError:
            messagebox.showerror("Missing dependency", "Install dependencies first:\n\npython -m pip install -r requirements.txt")
        except Exception as exc:
            messagebox.showerror("Wallet generation failed", str(exc))
            self._log(f"Wallet generation error: {exc}")

    def show_phrase(self):
        if not self.mnemonic:
            messagebox.showinfo("No phrase", "Generate a test wallet first.")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Recovery phrase — keep private")
        dialog.geometry("520x210")
        dialog.transient(self.root)
        dialog.grab_set()
        ttk.Label(dialog, text="Testnet recovery phrase", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=16, pady=(16, 6))
        ttk.Label(dialog, text="Anyone who obtains a recovery phrase can control the wallet it derives.", wraplength=480).pack(anchor="w", padx=16)
        phrase_var = tk.StringVar(value=self.mnemonic)
        entry = ttk.Entry(dialog, textvariable=phrase_var, width=66, show="•")
        entry.pack(fill="x", padx=16, pady=12)
        row = ttk.Frame(dialog)
        row.pack(fill="x", padx=16)
        def reveal():
            entry.configure(show="")
        def copy():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.mnemonic)
            messagebox.showinfo("Copied", "Phrase copied to clipboard. Clipboard contents may be visible to other apps.")
        ttk.Button(row, text="Reveal", command=reveal).pack(side="left")
        ttk.Button(row, text="Copy phrase", command=copy).pack(side="left", padx=8)
        ttk.Button(row, text="Close", command=dialog.destroy).pack(side="right")

    def clear_secrets(self):
        self.mnemonic = None
        self.wallet_data = {}
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_var.set("Local recovery phrase cleared from the app's active state.")
        self._log("Cleared the active mnemonic and derived-address list. Note: Python cannot guarantee secure memory erasure.")

    def copy_selected_address(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        if len(values) > 1:
            self.root.clipboard_clear()
            self.root.clipboard_append(values[1])
            self._log(f"Copied public address for {values[0]} to clipboard.")

    def check_balances(self):
        if not self.wallet_data:
            messagebox.showinfo("No wallet", "Generate a test wallet first.")
            return
        self.status_var.set("Checking public testnet endpoints…")
        for item in self.tree.get_children():
            vals = list(self.tree.item(item, "values"))
            vals[2] = "Checking…"
            self.tree.item(item, values=vals)
        threading.Thread(target=self._check_worker, daemon=True).start()

    def _rpc_eth_balance(self, rpc_url, address):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getBalance", "params": [address, "latest"]}
        r = requests.post(rpc_url, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(str(data["error"]))
        wei = int(data["result"], 16)
        return f"{Decimal(wei) / Decimal(10**18):.8f}"

    def _btc_balance(self, address):
        r = requests.get(f"{BTC_TESTNET_API}/address/{address}", timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        chain = data.get("chain_stats", {})
        mempool = data.get("mempool_stats", {})
        funded = int(chain.get("funded_txo_sum", 0)) + int(mempool.get("funded_txo_sum", 0))
        spent = int(chain.get("spent_txo_sum", 0)) + int(mempool.get("spent_txo_sum", 0))
        sats = funded - spent
        return f"{Decimal(sats) / Decimal(100_000_000):.8f}"

    def _check_worker(self):
        results = {}
        errors = {}
        for network, address in self.wallet_data.items():
            try:
                if network == "BTC Testnet":
                    results[network] = self._btc_balance(address) + " tBTC"
                elif network == "Ethereum Sepolia":
                    results[network] = self._rpc_eth_balance(ETH_SEPOLIA_RPC, address) + " Sepolia ETH"
                elif network == "BNB Smart Chain Testnet":
                    results[network] = self._rpc_eth_balance(BSC_TESTNET_RPC, address) + " testnet BNB"
            except Exception as exc:
                errors[network] = str(exc)
        self.root.after(0, lambda: self._apply_results(results, errors))

    def _apply_results(self, results, errors):
        for item in self.tree.get_children():
            network, address, _ = self.tree.item(item, "values")
            if network in results:
                balance = results[network]
                self.tree.item(item, values=(network, address, balance))
                self._log(f"{network}: {balance}")
            elif network in errors:
                self.tree.item(item, values=(network, address, "Unavailable"))
                self._log(f"{network} check failed: {errors[network]}")
        self.status_var.set("Balance check complete. These are testnet balances only; RPC/API services may be rate-limited.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WalletScannerApp(root)
    root.mainloop()
