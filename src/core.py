# By the end of Day 1, you should have:
#
# A working script (not a full app yet — no CLI, no encryption integration) that proves two things work independently:
#
# 1. Key derivation works and is repeatable
#
# python
# # crypto_utils.py
# def derive_key(password: str, salt: bytes) -> bytes:
#     # returns 32 bytes
#
# Test it manually: call it twice with the same password + same salt → same key both times. That's the whole correctness check for Day 1.
#
# 2. Database schema exists and CRUD works
# database.py
def init_db(): ...          # creates password_manager.db with the table
def add_entry(url, username, encrypted_password, salt): ...
def get_all_entries(): ...
def delete_entry(id): ...
#
# Test it manually: run a script that adds 2-3 fake rows (plaintext is fine for now, you're not encrypting yet — that's Day 2), then prints them back out from the DB. Open the .db file in PyCharm's built-in DB viewer or DB Browser for SQLite to confirm the table looks right.
#
# End-of-day checklist:
#
#  pip install cryptography works in your venv
#  derive_key() gives identical output for identical input, different output for different salt
#  SQLite file gets created with correct columns: id, url, username, password, salt, created_at
#  You can insert a row and query it back
#  No encryption yet — that's tomorrow. Today is just "can I generate a key" + "can I store/read a row"