import os
import sqlite3
from datetime import datetime

DB_NAME = "password_manager.db"


def init_db():
    """Create the entries table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # write the CREATE TABLE IF NOT EXISTS statement here
    # columns: id (INTEGER PRIMARY KEY AUTOINCREMENT), url, username, password, salt, created_at
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
    # hint: salt will be raw bytes -> use BLOB type for it
    # hint: created_at -> TEXT, you can default it or set it manually with datetime
    conn.commit()
    conn.close()


def add_entry(url: str, username: str, password: str, salt: bytes):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entries (url, username, password, salt, created_at) VALUES (?, ?, ?, ?, ?)",
        (url, username, password, salt, datetime.now().isoformat())
    )
    # NEVER f-strings (SQL injection)
    conn.commit()
    conn.close()


def get_all_entries():
    """Return all rows as a list."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # SELECT * FROM entries, then cursor.fetchall()
    cursor.execute("""SELECT url, username, password, salt FROM entries""")
    # r=cursor.fetchall()
    return cursor.fetchall()
    # conn.close()
    # return the list


def delete_entry(entry_id: int):
    """Delete one row by id."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # DELETE FROM entries WHERE id = ?
    cursor.execute("""delete from entries where id = ?""", (entry_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # init_db()
    # write your manual test here:
    # 1. add_entry(...) twice with fake data
    # 2. print(get_all_entries())
    # 3. confirm both rows show up with correct columns
    # add_entry("https://en.wikipedia.org","lol","1234324",b"ilove156422&^$")
    # add_entry("https://letterboxd.com","lol2","12343242",b"ilove156422&^$2")
    url=input("Enter the URL you wish to login to: ")
    username=input("Enter your username: ")
    password=input("Enter your password: ")
    salt=os.urandom(16)
    add_entry(url, username, password, salt)
    print(get_all_entries())

