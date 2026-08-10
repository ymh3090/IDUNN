import getpass
from src.db import init_db, add_entry, get_all_entries, get_decrypted_entry, update_entry, delete_entry
from cryptography.fernet import InvalidToken


def main():
    init_db()  # 1. make sure the table exists before anything else

    master_password = getpass.getpass("Enter master password: ")  # 2. unlock once, held in memory for the session
    # master_password=input("Enter master password: ")
    # 3. the menu loop — everything below reuses master_password, never asks again
    while True:
        print("""
╷ ╷┌─╴╷  ┌─╴┌─┐┌┬┐┌─╴   ╶┬╴┌─┐   ┌┬┐╷ ╷   ┌─┐┌─┐┌─┐┌─┐╷ ╷┌─┐┌─┐╶┬┐   ┌┬┐┌─┐┌┐╷┌─┐┌─╴┌─╴┌─┐
│╷│├╴ │  │  │ ││││├╴     │ │ │   │││└┬┘   ├─┘├─┤└─┐└─┐│╷││ │├┬┘ ││   │││├─┤│└┤├─┤│╶┐├╴ ├┬┘
└┴┘└─╴└─╴└─╴└─┘╵ ╵└─╴    ╵ └─┘   ╵ ╵ ╵    ╵  ╵ ╵└─┘└─┘└┴┘└─┘╵└╴╶┴┘   ╵ ╵╵ ╵╵ ╵╵ ╵└─┘└─╴╵└╴
""")


        print("\n1. Add entry\n2. List entries\n3. Delete entry\n4. Update entry\n5. Exit\n")
        choice = input("Choose: ")

        if choice == "1":
            website = input("Enter website: ").strip()
            usn = input("Enter username/email: ").strip()
            pwd = getpass.getpass("Enter password: ")
            if not website or not usn or not pwd:
                print("Website, username, and password can't be empty.")
                continue
            add_entry(website, usn, master_password, pwd)

        elif choice == "2":
            entries = get_all_entries()  # list of (id, url, username, encrypted_pwd, salt, created_at)
            for entry in entries:
                entry_id = entry[0]
                url = entry[1]
                username = entry[2]
                try:
                    decrypted_pwd = get_decrypted_entry(entry_id, master_password)
                    print(f"{entry_id} | {url} | {username} | {decrypted_pwd}")
                except InvalidToken:
                    print(f"{entry_id} | {url} | {username} | [WRONG MASTER PASSWORD]")


        elif choice == "3":
            print("\033[31m------------ Be Careful!! DELETING DATA!! ----------\033[0m")

            try:
                entry_id = int(input("Enter entry id to be DELETED: "))
            except ValueError:
                print("Invalid id — must be a number.")
                continue
            success = delete_entry(entry_id)
            if success:
                print("Deleted successfully")
            else:
                print(f"No entry with id {entry_id} found.")



        elif choice == "4":
            try:
                entry_id = int(input("Enter entry id to be DELETED: "))
            except ValueError:
                print("Invalid id — must be a number.")
                continue
            website = input("Enter new website: ")
            usn = input("Enter new username: ")
            pwd = getpass.getpass("Enter new password: ")
            success = update_entry(entry_id, website, usn, master_password, pwd)
            if not success:
                print(f"No entry with id {entry_id} found.")

        elif choice == "5":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()