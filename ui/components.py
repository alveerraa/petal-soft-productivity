import customtkinter as ctk
from ui.theme import BG, TEXT


class Card(ctk.CTkFrame):
    def __init__(self, parent, title):
        super().__init__(
            parent,
            fg_color="white",
            corner_radius=18
        )

        self.pack(padx=20, pady=12, fill="x")

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            text_color=TEXT,
            font=("Poppins", 14, "bold")
        )
        self.title_label.pack(anchor="w", padx=20, pady=(12, 4))
