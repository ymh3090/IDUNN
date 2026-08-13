import customtkinter as ctk
from src.password_utils import check_strength


class CheckerWindow(ctk.CTkToplevel):
    """Standalone password strength checker. No master password, no db access —
    only imports from password_utils, same rule as generator_window.py."""

    SCORE_LABELS = {0: "Weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong"}
    SCORE_COLORS = {0: "#e05555", 1: "#e05555", 2: "#e0a555", 3: "#a5c93a", 4: "#3ac96b"}

    def __init__(self, master):
        super().__init__(master)
        self.title("Password Checker")
        self.geometry("600x500")
        self.resizable(True, True)
        self.attributes("-topmost", True)
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self,
            text="Password",
            font=ctk.CTkFont(size=20),
        ).pack(pady=(20, 0))

        self.password_entry = ctk.CTkEntry(
            self,
            width=300,
            height=30,
            placeholder_text="Check a password's strength",
            font=ctk.CTkFont(size=20),
        )
        self.password_entry.pack(pady=10)
        self.password_entry.bind("<KeyRelease>", self.on_password_typed)

        self.strength_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=20))
        self.strength_label.pack(pady=5)

        self.warning_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13), text_color="#e0a555", wraplength=500,
        )
        self.warning_label.pack(pady=(0, 5))

        self.suggestions_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13), text_color="#8d8d8d", wraplength=500, justify="left",
        )
        self.suggestions_label.pack(pady=(0, 10))

    def on_password_typed(self, event=None):
        pwd = self.password_entry.get()
        if not pwd:
            self.strength_label.configure(text="")
            self.warning_label.configure(text="")
            self.suggestions_label.configure(text="")
            return

        result = check_strength(pwd)
        score = result["score"]

        self.strength_label.configure(
            text=f"Strength: {self.SCORE_LABELS[score]}  (crack time: {result['crack_time']})",
            text_color=self.SCORE_COLORS[score],
        )
        self.warning_label.configure(text=result["warning"])
        self.suggestions_label.configure(
            text="\n".join(result["suggestions"]) if result["suggestions"] else ""
        )


if __name__ == "__main__":
    # standalone test — normally opened from hub_window.py
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.withdraw()
    win = CheckerWindow(root)
    root.mainloop()