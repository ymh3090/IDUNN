# IDUNA — Local Password Manager

A local-first password manager built in Python. Stores website/service links,
usernames, and passwords — encrypted, on your own machine, nothing sent
anywhere. Includes a standalone password generator and strength checker.

Built as a learning project over about a week, using Claude for guidance on
architecture, debugging, and security best practices, while I wrote and
tested all the code myself.

---

## Features

- **Vault** — add, view, copy, and delete saved entries. Passwords are never
  shown on screen; they're copied to the clipboard on demand and the
  clipboard auto-clears after 20 seconds.
- **Master password** — unlocks the vault. Never stored anywhere, not even
  hashed — every unlock re-derives the encryption key from what you type.
  A wrong master password fails to decrypt cleanly; nothing is guessed or
  silently corrupted.
- **Password generator** — quick mode (length + symbols toggle) or custom
  mode (exact count of uppercase/lowercase/digits/special characters).
  Uses Python's `secrets` module — cryptographically secure, not `random`.
- **Password strength checker** — live feedback as you type, powered by
  `zxcvbn` (pattern-based analysis: dictionary words, keyboard walks,
  sequences, repeats — not naive character-type counting).
- **Desktop GUI** — built with `customtkinter`. A hub screen links to three
  independent tools: Vault, Generator, Checker.

---

## Security design

- **Argon2id** for key derivation (master password → encryption key),
  tuned to meet OWASP's current minimum recommendation (iterations=2,
  memory_cost=64MB, well above their 19MB floor).
- **Fernet (AES-128-CBC + HMAC-SHA256)** for encrypting each stored
  password. Every entry gets its own random salt, so identical passwords
  never produce identical ciphertext.
- The master password is used only in memory, per session, to re-derive
  the key on demand. It is never written to disk in any form.
- No custom cryptography — every primitive here is from the `cryptography`
  library, chosen deliberately over hand-rolled alternatives.

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

`generator_window.py` and `checker_window.py` only import from
`password_utils.py` — they have no access to the vault, the database, or
the master password. They work standalone, with no data ever unlocked.

---

## Setup

```bash
git clone <repo-url>
cd password_manager
pip install -r requirements.txt
python main.py
```

### Dependencies
- `customtkinter` — GUI
- `cryptography` — Argon2id key derivation, Fernet encryption
- `zxcvbn` — password strength analysis
- `pyperclip` — clipboard copy for passwords and generated results

---

## How it works, briefly

1. On first run, `init_db()` creates a local SQLite database with one
   `entries` table (id, url, username, encrypted password, salt, created_at).
2. Opening the Vault prompts for a master password. If entries already
   exist, it's verified by attempting to decrypt one — there is no stored
   hash or check of the master password itself.
3. Adding an entry: a fresh random salt is generated, the master password
   that salt derive a one-time encryption key via Argon2id, and the
   entry's password is encrypted with Fernet before being written to disk.
4. Reading a password back: the same master password + that entry's
   stored salt re-derive the exact same key, and Fernet decrypts it. A
   wrong master password produces a hard `InvalidToken` failure — no
   partial or garbled plaintext is ever returned.