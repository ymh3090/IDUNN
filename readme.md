# Iðunn (IDUNN) 

A desktop password manager built with Python and CustomTkinter. Store your logins in an encrypted vault, generate cryptographically secure passwords, and check how strong your existing ones really are
all in one app, no cloud, no tracking.

## Features

- **Vault**: add, view, copy, and delete saved entries. Passwords are never
  shown on screen; they're copied to the clipboard on demand and the
  clipboard auto-clears.
- **Master password**: unlocks the vault. Never stored anywhere, not even
  hashed every unlock re-derives the encryption key from what you type.
  A wrong master password fails to decrypt cleanly; nothing is guessed or
  silently corrupted.
- **Password generator**: quick mode or custom mode (exact count of uppercase/lowercase/digits/special characters).
  Uses Python's `secrets` module.
- **Password strength checker**: live feedback as you type, powered by
  `zxcvbn` (pattern-based analysis: dictionary words, keyboard walks,
  sequences, repeats.
- **Desktop GUI**: built with `customtkinter`. A hub screen links to three
  independent tools: Vault, Generator, Checker.

---

## Security design

- **Argon2id** for key derivation (master password → encryption key),
  tuned to meet OWASP's current minimum recommendation (iterations=2,
  memory_cost=64MB, well above their 19MB floor).
- **Fernet (AES-128-CBC + HMAC-SHA256)** for encrypting each stored
  password. Every entry gets its own random salt, so identical passwords
  never produce identical ciphertext.
- The master password is used only per session, to re-derive
  the key on demand. It is never written to disk in any form.

---

## Project structure

```
main.py                  Entry point — launches the hub window
hub_window.py             Landing screen — Vault / Generator / Checker
login_window.py           Master password prompt, unlocks the vault
vault_window.py            Add / list / copy / delete saved entries
generator_window.py        Standalone password generator
checker_window.py          Standalone password strength checker

src/
  crypto_utils.py          Key derivation (Argon2id) and encrypt/decrypt (Fernet)
  db.py                    SQLite storage — all entries encrypted before write
  password_utils.py        Password generation and zxcvbn-based strength checking
```

---
## Setup

```bash
git clone https://github.com/ymh3090/IDUNN
pip install customtkinter cryptography zxcvn pyperclip
cd password_manager
python main.py
```
or u can download the executable file in the releases file to run the app directly

## How it works, briefly

1. On first run, we create a local SQLite database with one
   table.
2. Opening the Vault prompts for a master password. If entries already
   exist, it's verified by attempting to decrypt one **there is no stored
   hash or check of the master password itself.**
3. Adding an entry: a fresh random salt is generated, the master password
   that salt derive a one-time encryption key via Argon2id, and the
   entry's password is encrypted with Fernet before being written to disk.
4. Reading a password back: the same master password + that entry's
   stored salt re-derive the exact same key, and Fernet decrypts it.

***
## Contributing
It's a personal side project, but if you spot a bug or a security issue,
open an issue or PR  especially if it's the security kind. Feedback on the crypto choices is very welcome.