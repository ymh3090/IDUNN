import customtkinter as ctk
import pyperclip
import threading

from src.password_utils import generate_password, generate_custom_password


class GeneratorWindow(ctk.CTkToplevel):
    """Standalone password generator. No master password, no db access —
    only imports from password_utils, same rule as checker_window.py."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Password Generator")
        self.geometry("600x700")
        self.attributes("-topmost", True)
        self._build_ui()

    def _build_ui(self):
        # ---------------- Quick generate ----------------
        ctk.CTkLabel(self, text="Quick Generate", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 5))

        self.length_label = ctk.CTkLabel(self, text="Length: 14")
        self.length_label.pack()

        self.length_slider = ctk.CTkSlider(
            self, from_=8, to=32, number_of_steps=24, command=self.on_slider_move
        )
        self.length_slider.set(14)
        self.length_slider.pack(pady=5)

        self.symbols_switch = ctk.CTkSwitch(self, text="Include symbols")
        self.symbols_switch.select()  # on by default
        self.symbols_switch.pack(pady=10)

        ctk.CTkButton(self, text="Generate", command=self.on_quick_generate).pack(pady=10)

        # ---------------- Custom generate ----------------
        ctk.CTkLabel(self, text="Custom Generate", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(25, 5))
        ctk.CTkLabel(self, text="Exact count of each character type", text_color="#8d8d8d").pack()

        counts_frame = ctk.CTkFrame(self, fg_color="transparent")
        counts_frame.pack(pady=10)

        self.upper_slider, self.upper_count_label = self._labeled_count_slider(counts_frame, "Uppercase", 0)
        self.lower_slider, self.lower_count_label = self._labeled_count_slider(counts_frame, "Lowercase", 1)
        self.digit_slider, self.digit_count_label = self._labeled_count_slider(counts_frame, "Digits", 2)
        self.special_slider, self.special_count_label = self._labeled_count_slider(counts_frame, "Special", 3)

        ctk.CTkButton(self, text="Generate custom", command=self.on_custom_generate).pack(pady=10)

        # ---------------- Result ----------------
        ctk.CTkLabel(self, text="Result", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(25, 5))

        self.result_entry = ctk.CTkEntry(self, width=500,state="readonly")
        self.result_entry.pack(pady=5)

        ctk.CTkButton(self, text="Copy to clipboard", command=self.copy_result).pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="", text_color="#e05555")
        self.status_label.pack(pady=5)

    def _labeled_count_slider(self, parent, label_text: str, column: int):
        """Builds one 'label + live count + slider' triple inside a grid.
        Returns (slider, count_label) — the caller reads slider.get() at click
        time, never here, so it always reflects the user's current choice."""
        col_frame = ctk.CTkFrame(parent, fg_color="transparent")
        col_frame.grid(row=0, column=column, padx=8)

        ctk.CTkLabel(col_frame, text=label_text, font=ctk.CTkFont(size=12)).pack()
        count_label = ctk.CTkLabel(col_frame, text="0")
        count_label.pack()

        slider = ctk.CTkSlider(
            col_frame, from_=0, to=15, number_of_steps=10, width=100,
            command=lambda value, lbl=count_label: lbl.configure(text=str(int(value))),
        )
        slider.set(0)
        slider.pack(pady=(0, 5))
        return slider, count_label

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def on_slider_move(self, value):
        self.length_label.configure(text=f"Length: {int(value)}")

    def on_quick_generate(self):
        length = int(self.length_slider.get())
        use_symbols = bool(self.symbols_switch.get())  # read at click time, not build time
        pwd = generate_password(length, use_symbols)
        self._show_result(pwd)

    def on_custom_generate(self):
        upper = int(self.upper_slider.get())
        lower = int(self.lower_slider.get())
        digit = int(self.digit_slider.get())
        special = int(self.special_slider.get())

        try:
            pwd = generate_custom_password(upper, lower, digit, special)
        except ValueError as e:
            self.status_label.configure(text=str(e))  # "At least one character count must be greater than 0"
            return

        self._show_result(pwd)

    def _show_result(self, pwd: str):
        self.status_label.configure(text="")
        self.result_entry.configure(state="normal")
        self.result_entry.delete(0, "end")
        self.result_entry.insert(0, pwd)
        self.result_entry.configure(state="readonly")

    def copy_result(self):
        pwd = self.result_entry.get()
        if not pwd:
            self.status_label.configure(text="Generate a password first.")
            return
        pyperclip.copy(pwd)
        self.status_label.configure(text="Copied! Clearing in 20 seconds...", text_color="#3ac96b")
        threading.Timer(20, lambda: pyperclip.copy("")).start()


if __name__ == "__main__":
    # standalone test — normally opened from hub_window.py
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.withdraw()  # hide the throwaway root, only show the Toplevel
    win = GeneratorWindow(root)
    root.mainloop()