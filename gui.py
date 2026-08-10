import customtkinter as ctk


import customtkinter

def button_callback():
    print("button clicked")

app = customtkinter.CTk()
app.geometry("1000x700")
app.resizable(False, False)

customtkinter.deactivate_automatic_dpi_awareness()
button = customtkinter.CTkButton(
    app,
    text="click me!",
    command=button_callback,
    width=200,
    height=200,
    corner_radius=100,  # Half of width/height makes a perfect circle
    hover_color="red",   # Corrected spelling
    bg_color="pink",
    text_color="black",
    text_color_disabled="red",
)

button.pack(padx=200, pady=200)
textbox = ctk.CTkTextbox(master=app, width=300, height=200, corner_radius=8)
textbox.pack(padx=200, pady=200)

app.mainloop()