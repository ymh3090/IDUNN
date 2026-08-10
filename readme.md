# Password Manager — Progress Log

Local password manager storing: website/game link, username/email, password.
Built solo in Python. No custom crypto — vetted primitives only (`cryptography` lib).

## Stack
- `cryptography` — Argon2id (key derivation) + Fernet (encryption)
- `sqlite3` — local storage
- CLI first, GUI later

---

## Day 1 — Foundations

**Goal:** prove two independent pieces work before wiring them together.

### `crypto_utils.py`
- `generate_salt()` → `os.urandom(16)`, random bytes unique per entry
- `derive_key(password, salt)` → runs Argon2id, returns 32 raw bytes
- Tested: same password + same salt → same key. Different password → different key.

### `database.py`
- `init_db()` → creates `entries` table if it doesn't exist
- `add_entry()`, `get_all_entries()`, `delete_entry()` → basic CRUD
- Schema:
  ```sql
  CREATE TABLE IF NOT EXISTS entries (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      url TEXT NOT NULL,
      username TEXT NOT NULL,
      password BLOB NOT NULL,
      salt BLOB NOT NULL,
      created_at TEXT NOT NULL
  )
  ```
- Password/salt stored as `BLOB` since they'll hold encrypted bytes later.
- Tested: inserted rows, read them back correctly as tuples.

**Bugs hit and fixed:**
- `INSERT INTO entries VALUES (?, ?, ?, ?)` failed — table has 6 columns, only 4 values given. Fixed by naming columns explicitly and supplying `created_at` via `datetime.now().isoformat()`.
- `get_all_entries()` returned a closed cursor object instead of data — `fetchall()`'s return value was never captured. Fixed by assigning it to `rows` and returning `rows`.

---

## Day 2 — Encryption integration (in progress)

**Goal:** wire crypto into storage so passwords are never written in plaintext.

### Key concept: Fernet needs a base64-encoded key
Fernet doesn't accept the raw 32 bytes `derive_key()` produces — it needs
`base64.urlsafe_b64encode()` applied first. This was the missing piece from Day 1's `derive_key()`.

```python
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = Argon2id(salt=salt, length=32, iterations=1, lanes=4, memory_cost=64 * 1024)
    raw_key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(raw_key)
```

### `encrypt()` / `decrypt()` — added to `crypto_utils.py`
```python
def encrypt(data: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt(token: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(token).decode()
```
Tested: encrypt → decrypt round-trip returns the original string, using two
*separately derived* keys (same password + salt) to simulate real unlock behavior.

### `add_entry()` — wired to crypto
```python
def add_entry(url: str, username: str, master_password: str, entry_password: str):
    salt = generate_salt()
    key = derive_key(master_password, salt)
    encrypted_password = encrypt(entry_password, key)
    # ... INSERT with encrypted_password + salt
```
Signature takes two different passwords — don't confuse them:
- `master_password`: yours, unlocks everything, never stored
- `entry_password`: the site's password, gets encrypted before storage

### `get_decrypted_entry()` — read path
Pulls `password, salt` for a row, re-derives the key from `master_password` + that
row's stored salt, decrypts, returns plaintext.

### Day 2 core test — PASSED ✅
- Correct master password → decrypts back to exact original (`yayanuts123`)
- Wrong master password → `cryptography.fernet.InvalidToken` crash, no silent garbage returned

This is the security property that matters: Fernet signs (HMAC) as well as encrypts,
so a wrong key fails loudly instead of producing plausible-looking wrong plaintext.
Deliberately left this crash raw (no try/except) for testing — friendly error handling
comes in Day 3 when building the CLI.

### Day 2 — remaining todos
- [ ] `get_all_entries()` still missing `conn.close()` — leaks the connection every call
- [ ] Delete old Day 1 plaintext test rows sitting in `password_manager.db` (predate encryption)
- [ ] `update_entry()` still takes a raw `password` param — needs to re-derive + re-encrypt
      like `add_entry()` does, not accept an already-processed value

### `update_entry()` — bugs caught while drafting (now fixed for basic wiring, re-encryption still TODO above)
Trailing comma before `WHERE`, mismatched placeholder/value order, missing
`commit()`/`close()`, and updating by `url` instead of `id` (unsafe — `url` isn't
unique, could update multiple rows unintentionally). Current version updates by `id`,
matching `delete_entry()`'s pattern — but still needs the encrypt-before-store step.

---

## Archived scratch code (Day 1, `crypto_utils.py`)
Old exploratory code kept here for reference instead of cluttering the working file.

```python
# import hashlib
# import base64
# import os
# from Crypto.Cipher import AES
# from Crypto.Hash import SHA256
# from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
# salt = os.urandom(16)
# kdf = Argon2id(
#     salt=salt,length=32,iterations=1,lanes=4,memory_cost=64 * 1024,ad=None,secret=None,
# )
#
# key = kdf.derive(b"my great password")
# # verify
# kdf = Argon2id(
#     salt=salt,
#     length=32,
#     iterations=1,
#     lanes=4,
#     memory_cost=64 * 1024,
#     ad=None,
#     secret=None,
# )
# kdf.verify(b"my great password", key)
#
# Fernet implementation notes (from docs):
# - AES in CBC mode with a 128-bit key for encryption; PKCS7 padding.
# - HMAC using SHA256 for authentication.
# - Initialization vectors generated using os.urandom().
```

---

## Day 3 — CLI + master password flow

**Goal:** turn the tested functions into an actual runnable program — unlock once with a
master password, then add/list/update/delete during that session.

### `main.py`
- `init_db()` runs first, then `getpass.getpass()` prompts for the master password once —
  held in memory for the session, never re-asked, never stored to disk
- Menu loop: Add, List, Delete, Update, Exit
- `add_entry()` signature takes two different passwords — kept distinct on purpose:
  - `master_password`: unlocks everything, never stored
  - `entry_password`: the site's password, gets encrypted before storage

### Bugs caught and fixed during CLI build
- `update_entry()` / `delete_entry()` silently no-op'd on a nonexistent id — no error,
  no feedback, just did nothing. Fixed by checking `cursor.rowcount > 0` and returning
  a bool so the CLI can report "No entry with id X found."
- Non-numeric id input (`int(input(...))`) crashed with `ValueError` — wrapped in
  try/except with `continue` to loop back cleanly instead of crashing
- Empty website/username/password allowed a blank "ghost" entry — added a check
  rejecting empty fields before calling `add_entry()`
- Duplicate `elif choice == "4":` block in main.py (dead code from early drafting) — removed

### Automated testing
Manual CLI testing (typing into the menu each time) was replaced with `unittest`:
```
python -m unittest test_db.py -v
```
Covers: add+decrypt round-trip, wrong master password raises, delete/update on
nonexistent id return False, delete doesn't shift surrounding ids. All passing.

### Verified through manual stress-testing
- Ids don't shift or corrupt on delete
- Wrong master password across a full session correctly fails on every old entry,
  no silent garbage decryption
- Unicode/emoji in fields round-trip correctly
- Duplicate entries get separate ids and separate salts (salts never repeat)

---

## Day 4 — Hardening

**Goal:** reduce exposure of decrypted passwords and confirm crypto params meet
current security recommendations.

### Clipboard copy instead of printing to screen
Redesigned "List entries" to show only `id | url | username` — **never the password**.
Added a separate "Copy password" menu option that decrypts one entry on demand and
sends it to the clipboard only.

```python
def copy_with_clear(text: str, delay: int = 20):
    pyperclip.copy(text)
    print(f"Password copied to clipboard. Clearing in {delay} seconds...")
    threading.Timer(delay, lambda: pyperclip.copy('')).start()
```
Verified manually: password pastes correctly right after copy, clipboard is empty
after the 20s delay elapses.

Rationale for the split (list = metadata only, copy = separate action): printing
passwords to the terminal defeats hardening even with clipboard auto-clear — terminal
scrollback and shoulder-surfing are still exposed. Only the clipboard entry point
handles decrypted plaintext, and only briefly.

### KDF parameter review against OWASP
Checked `derive_key()`'s Argon2id settings against the OWASP Password Storage Cheat
Sheet's current minimum recommendation (memory ≥19 MiB, iterations ≥2, parallelism 1).

| Param | Was | OWASP min | Action |
|---|---|---|---|
| `memory_cost` | 64 MB | 19 MB | Already above minimum — kept as-is |
| `iterations` | 1 | 2 | **Bumped to 2** — was below the floor |
| `lanes` | 4 | — | Fine, matches typical multi-core guidance |

Not unit-tested directly — parameter values aren't a behavior to assert, they're a
tuning decision. Existing `test_db.py` suite (round-trip, wrong-password-fails) still
passes after the change, confirming correctness wasn't affected.

### Notes on entries — multiple accounts per site
Confirmed the schema already supports multiple entries for the same `url` (no unique
constraint on it) — e.g. two Gmail accounts just become two separate rows with
different ids and salts. Worth remembering if a future "look up by url" feature is
added: it must return a list of matches, not assume one.
