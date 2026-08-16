import customtkinter as ctk
from cryptography.fernet import InvalidToken
import pyperclip
import threading
from src.db import get_all_entries, add_entry, delete_entry, get_decrypted_entry
from src.password_utils import generate_password, check_strength


class VaultWindow(ctk.CTkToplevel):
    """Main screen after unlock. Shows entries (no passwords shown here),
    lets you add/copy/delete. master_password is held in memory only,
    passed in from the login screen, never written to disk."""

    def __init__(self, master, master_password: str):
        super().__init__(master)  # master = the parent window (login window)
        self.master_password = master_password

        self.title("The Vault")
        self.geometry("900x600")

        self._build_static_ui()
        self.refresh_list()

    def _build_static_ui(self):
        header = ctk.CTkLabel(
            self,
            text="Your Vault",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        header.pack(pady=(20, 10))

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=820, height=420)
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        add_button = ctk.CTkButton(
            self,
            text="+ Add entry",
            command=self.open_add_entry_popup,
        )
        add_button.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="", text_color="#e05555")
        self.status_label.pack(pady=5)

    def refresh_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()  # clear old rows before rebuilding

        entries = get_all_entries()

        if not entries:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No entries yet — add your first one",
                text_color="#8d8d8d",
            ).pack(pady=20)
            return

        for entry in entries:
            entry_id, url, username = entry[0], entry[1], entry[2]
            self._build_entry_row(entry_id, url, username)

    def _build_entry_row(self, entry_id: int, url: str, username: str):
        row = ctk.CTkFrame(self.scroll_frame)
        row.pack(fill="x", pady=5, padx=5)


        info_text = f"{url}  |  UserName: {username}"

        ctk.CTkLabel(row, text=info_text, anchor="w").pack(side="left", padx=10, pady=8)

        # entry_id=entry_id defaults the argument at lambda-creation time —
        # without this every button would reference the LAST loop's entry_id
        delete_btn = ctk.CTkButton(
            row, text="Delete", width=70, fg_color="#b23b3b", hover_color="#8f2f2f",
            command=lambda entry_id=entry_id: self.delete_and_refresh(entry_id),
        )
        delete_btn.pack(side="right", padx=5, pady=5)

        copy_btn = ctk.CTkButton(
            row, text="Copy password", width=110,
            command=lambda entry_id=entry_id: self.copy_password(entry_id),
        )
        copy_btn.pack(side="right", padx=5, pady=5)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def delete_and_refresh(self, entry_id: int):
        delete_entry(entry_id)
        self.refresh_list()

    def copy_password(self, entry_id: int):
        try:
            decrypted = get_decrypted_entry(entry_id, self.master_password)
        except InvalidToken:
            self.status_label.configure(text="Wrong master password — can't decrypt this entry.", text_color="#e05555")
            return
        except ValueError as e:
            self.status_label.configure(text=str(e), text_color="#e05555")
            return

        pyperclip.copy(decrypted)
        self.status_label.configure(text="Copied! Clearing in 20 seconds...", text_color="#3ac96b")
        threading.Timer(20, lambda: pyperclip.copy("")).start()

    def open_add_entry_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add entry")
        popup.geometry("400x420")
        popup.attributes("-topmost", True)  # keep popup above the main window

        ctk.CTkLabel(popup, text="Website").pack(pady=(20, 0))
        website_entry = ctk.CTkEntry(popup, width=300)
        website_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Username / email / Phone").pack(pady=(10, 0))
        username_entry = ctk.CTkEntry(popup, width=300)
        username_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Password").pack(pady=(10, 0))
        password_entry = ctk.CTkEntry(popup, width=300, show="*")
        password_entry.pack(pady=5)

        strength_label = ctk.CTkLabel(popup, text="")
        strength_label.pack(pady=5)

        score_labels = {0: "Weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong"}
        score_colors = {0: "#e05555", 1: "#e05555", 2: "#e0a555", 3: "#a5c93a", 4: "#3ac96b"}

        def on_password_typed(event=None):
            pwd = password_entry.get()
            if not pwd:
                strength_label.configure(text="")
                return
            result = check_strength(pwd)
            score = result["score"]
            strength_label.configure(
                text=f"Strength: {score_labels[score]}  (crack time: {result['crack_time']})",
                text_color=score_colors[score],
            )

        password_entry.bind("<KeyRelease>", on_password_typed)

        def on_generate():
            new_pwd = generate_password(14)
            password_entry.delete(0, "end")
            password_entry.insert(0, new_pwd)
            on_password_typed()  # update the strength label immediately

        generate_btn = ctk.CTkButton(popup, text="Generate one", command=on_generate)
        generate_btn.pack(pady=10)

        status_label = ctk.CTkLabel(popup, text="", text_color="#e05555")
        status_label.pack(pady=5)

        def on_save():
            website = website_entry.get().strip()
            username = username_entry.get().strip()
            pwd = password_entry.get()

            if not website or not username or not pwd:
                status_label.configure(text="All fields are required.")
                return

            add_entry(website, username, self.master_password, pwd)
            popup.destroy()
            self.refresh_list()

        save_btn = ctk.CTkButton(popup, text="Save", command=on_save)
        save_btn.pack(pady=15)


# if __name__ == "__main__":
#     ctk.set_appearance_mode("dark")
#     app = VaultWindow(master_password="masterpw")
#     app.mainloop()
