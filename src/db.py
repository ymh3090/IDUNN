import sqlite3
from datetime import datetime
from src.crypto_utils import derive_key, encrypt, decrypt, generate_salt

DB_NAME = "password_manager.db"


def init_db():
    """Create the entries table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    username TEXT NOT NULL,
    password BLOB NOT NULL,
    salt BLOB NOT NULL,
    created_at TEXT NOT NULL
    )
                        """)
    conn.commit()
    conn.close()


def add_entry(url: str, username: str, master_password: str, entry_password: str):
    """Encrypts entry_password using a key derived from master_password + a fresh salt,
    then stores the encrypted bytes. master_password itself is never stored."""
    salt = generate_salt()
    key = derive_key(master_password, salt)
    encrypted_password = encrypt(entry_password, key)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entries (url, username, password, salt, created_at) VALUES (?, ?, ?, ?, ?)",
        (url, username, encrypted_password, salt, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def update_entry(entry_id: int, url: str, username: str, master_password: str, entry_password: str) -> bool:
    salt = generate_salt()
    key = derive_key(master_password, salt)
    encrypted_password = encrypt(entry_password, key)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE entries SET url=?, username=?, password=?, salt=? WHERE id=?",
        (url, username, encrypted_password, salt, entry_id)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def get_all_entries():
    """Return all rows as a list. Password column will be encrypted bytes, not plaintext."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, username, password, salt, created_at FROM entries")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_decrypted_entry(entry_id: int, master_password: str):
    """Fetch one row and decrypt its password using master_password + that row's stored salt."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password, salt FROM entries WHERE id=?", (entry_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise ValueError(f"No entry with id {entry_id}")

    encrypted_password, salt = row
    key = derive_key(master_password, salt)
    return decrypt(encrypted_password, key)


def delete_entry(entry_id: int) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


if __name__ == "__main__":
    init_db()

    result = get_decrypted_entry(1, "nuts123")
    print("Decrypted:", result)

    # Deliberately left raw (no try/except) — confirms Fernet fails loudly on wrong key.
    # Uncomment to re-test:
    # print(get_decrypted_entry(1, "wrong_password"))
