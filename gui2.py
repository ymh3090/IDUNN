import customtkinter


class HackerButtonApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x400")
        self.title("Uiverse Animation in CTk")
        self.configure(fg_color="#1a1a1a")  # Dark theme background

        # Match CSS styling properties
        self.default_text = "Button"
        self.bg_color = "#292929"
        self.hover_bg_color = "#333333"
        self.text_color = "#ffffff"
        self.hover_text_color = "#FAC921"
        self.font_family = "Menlo"  # Falls back to standard monospace if missing

        # CSS Scramble Timeline translated to a sequential frame list
        self.scramble_frames = [
            "#", ".", "^{", "-!", "#$_", "№:0", "#{+.", "@}-?",
            "?{4@%", "=.,^!", "?2@%", "\;1}]", "?{%:%", "|{f[4",
            "{4%0%", "'1_0<", "{0%", "]>'", "4", "2", ""
        ]
        self.animation_index = 0
        self.is_hovered = False

        # Create the CustomTkinter Button
        self.button = customtkinter.CTkButton(
            self,
            text=self.default_text,
            fg_color=self.bg_color,
            hover_color=self.hover_bg_color,
            text_color=self.text_color,
            font=(self.font_family, 16, "bold"),
            width=140,
            height=50,
            corner_radius=4,
            command=self.button_callback
        )
        self.button.place(relx=0.5, rely=0.5, anchor="center")

        # Bind hover events
        self.button.bind("<Enter>", self.on_hover)
        self.button.bind("<Leave>", self.on_leave)

    def on_hover(self, event):
        """Triggers immediately when mouse enters button space."""
        self.is_hovered = True
        self.button.configure(text_color=self.hover_text_color)
        self.animation_index = 0
        self.run_scramble_animation()

    def on_leave(self, event):
        """Resets button state instantly when mouse leaves."""
        self.is_hovered = False
        self.button.configure(text_color=self.text_color, text=self.default_text)

    def run_scramble_animation(self):
        """Cycles through the scramble frame timeline using an asynchronous loop."""
        # Halt execution if user moved mouse away mid-animation
        if not self.is_hovered:
            return

        if self.animation_index < len(self.scramble_frames):
            # Overlay symbols over original text or just replace it
            current_symbol = self.scramble_frames[self.animation_index]

            if current_symbol == "":
                self.button.configure(text=self.default_text)
            else:
                self.button.configure(text=f"{self.default_text} {current_symbol}")

            self.animation_index += 1

            # 1200ms duration split evenly across 21 frames ≈ 57ms per step
            self.after(57, self.run_scramble_animation)

    def button_callback(self):
        print("Button Clicked!")


if __name__ == "__main__":
    app = HackerButtonApp()
    app.mainloop()
