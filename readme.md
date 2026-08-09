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

### Still to do
- Wire `add_entry()` in `database.py` to call `derive_key()` + `encrypt()` before inserting
- Add a decrypt path for reading entries back
- Confirm wrong master password fails to decrypt (expected behavior, not a bug)
- Remove old Day 1 plaintext test rows from the DB

### `update_entry()` — drafted, needs fixes
Bugs caught: trailing comma before `WHERE`, mismatched placeholder/value order,
missing `commit()`/`close()`, and updating by `url` instead of `id` (unsafe —
`url` isn't unique, could update multiple rows unintentionally).

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
# ).
# kdf.verify(b"my great password", key)
#
# Fernet implementation notes (from docs):
# - AES in CBC mode with a 128-bit key for encryption; PKCS7 padding.
# - HMAC using SHA256 for authentication.
# - Initialization vectors generated using os.urandom().
```

## Notes / decisions
- Table named `entries`, not `passwords` — avoids drawing attention to the file's purpose.
- Master password / derived key is never written to disk — only the salt is stored per entry.
- Rule for the whole project: no custom crypto. Vetted primitives only (Fernet, Argon2id).