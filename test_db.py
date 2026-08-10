# test_db.py
import unittest
import os
from src.db import init_db, add_entry, get_all_entries, get_decrypted_entry, update_entry, delete_entry, DB_NAME

class TestDB(unittest.TestCase):
    def setUp(self):
        # fresh DB before every test, so tests don't interfere with each other
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        init_db()

    def test_add_and_decrypt(self):
        add_entry("test.com", "user1", "masterpw", "secret123")
        entries = get_all_entries()
        entry_id = entries[0][0]
        decrypted = get_decrypted_entry(entry_id, "masterpw")
        self.assertEqual(decrypted, "secret123")

    def test_wrong_master_password_raises(self):
        add_entry("test.com", "user1", "masterpw", "secret123")
        entry_id = get_all_entries()[0][0]
        with self.assertRaises(Exception):  # InvalidToken
            get_decrypted_entry(entry_id, "wrongpw")

    def test_delete_nonexistent_id(self):
        result = delete_entry(9999)
        self.assertFalse(result)

    def test_update_nonexistent_id(self):
        result = update_entry(9999, "x.com", "u", "masterpw", "pw")
        self.assertFalse(result)

    def test_delete_does_not_shift_ids(self):
        add_entry("a.com", "u1", "mp", "p1")
        add_entry("b.com", "u2", "mp", "p2")
        add_entry("c.com", "u3", "mp", "p3")
        ids = [e[0] for e in get_all_entries()]
        delete_entry(ids[1])  # delete the middle one
        remaining_ids = [e[0] for e in get_all_entries()]
        self.assertEqual(remaining_ids, [ids[0], ids[2]])

if __name__ == "__main__":
    unittest.main()