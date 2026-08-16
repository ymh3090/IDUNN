import customtkinter as ctk

from login_window import LoginWindow
from generator_window import GeneratorWindow
from checker_window import CheckerWindow


class HubWindow(ctk.CTk):
    """The ONLY ctk.CTk() root in the whole app. Every other window
    (Login, Vault, Generator, Checker) must inherit from ctk.CTkToplevel
    and take `master` as their first constructor argument — never
    create a second ctk.CTk() root, that's what caused the
    'invalid command name ...check_dpi_scaling' crash earlier."""

    def __init__(self):
        super().__init__()
        self.title("IDUNN")
        self.geometry("500x400")
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="IDUNN", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=30)
        ctk.CTkButton(self, text="Vault", command=self.open_vault).pack(pady=10)
        ctk.CTkButton(self, text="Password Generator", command=self.open_generator).pack(pady=10)
        ctk.CTkButton(self, text="Password Checker", command=self.open_checker).pack(pady=10)

    def open_vault(self):
        LoginWindow(self)

    def open_generator(self):
        GeneratorWindow(self)

    def open_checker(self):
        CheckerWindow(self)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = HubWindow()
    app.mainloop()