import customtkinter as ctk
from PIL import Image
import os

# -----------------------------
# BASIC APP CONFIG
# -----------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")  # we'll override colors manually

APP_WIDTH = 420
APP_HEIGHT = 720


class PetalApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Petal 🌸")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)

        # Center window on Mac
        self.center_window()

        # Load all images
        self.images = {}
        self.load_images()

        # Build UI
        self.build_ui()

    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (APP_WIDTH // 2)
        y = (self.winfo_screenheight() // 2) - (APP_HEIGHT // 2)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}+{x}+{y}")

    # -----------------------------
    # IMAGE LOADER
    # -----------------------------
    def load_images(self):
        base_path = os.path.join(os.path.dirname(__file__), "assets")

        # Focus flower
        self.images["focus_flower"] = ctk.CTkImage(
            Image.open(os.path.join(base_path, "focus_flower.png")),
            size=(80, 80)
        )

        # Mood icons
        self.images["mood"] = {
            "sleepy": self.load_icon("icons/sleepy.png"),
            "motivated": self.load_icon("icons/motivated.png"),
            "angry": self.load_icon("icons/angry.png"),
            "sad": self.load_icon("icons/sad.png"),
        }

        # Decorative icons
        self.images["deco"] = {
            "d1": self.load_icon("icons/deco1.png", (40, 40)),
            "d2": self.load_icon("icons/deco2.png", (40, 40)),
            "d3": self.load_icon("icons/deco3.png", (40, 40)),
            "d4": self.load_icon("icons/deco4.png", (40, 40)),
        }

        # Garden plants
        self.images["plants"] = {}
        plant_types = ["rose", "hydrangea", "sunflower"]
        stages = ["seed", "grow", "bloom"]

        for plant in plant_types:
            self.images["plants"][plant] = {}
            for stage in stages:
                path = f"plants/{plant}_{stage}.png"
                self.images["plants"][plant][stage] = self.load_icon(path, (48, 48))

    def load_icon(self, relative_path, size=(32, 32)):
        base_path = os.path.join(os.path.dirname(__file__), "assets")
        full_path = os.path.join(base_path, relative_path)
        return ctk.CTkImage(Image.open(full_path), size=size)

    # -----------------------------
    # UI LAYOUT (SKELETON)
    # -----------------------------
    def build_ui(self):
        # App background frame
        self.main_frame = ctk.CTkFrame(self, fg_color="#f7f4fb")
        self.main_frame.pack(fill="both", expand=True)

        # Title
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(pady=(20, 10))

        ctk.CTkLabel(
            title_frame,
            text="petal 🌸",
            font=("SF Pro Rounded", 28, "bold"),
            text_color="#5a4b81"
        ).pack()

        ctk.CTkLabel(
            title_frame,
            text="go gently today",
            font=("SF Pro Rounded", 12),
            text_color="#8a80a8"
        ).pack()

        # Decorative icon near title
        ctk.CTkLabel(
            title_frame,
            image=self.images["deco"]["d1"],
            text=""
        ).place(x=260, y=-5)

        # Cards container
        self.cards_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cards_container.pack(padx=20, pady=10, fill="both", expand=True)

        # Placeholder cards
        self.create_card("Focus")
        self.create_card("Mood + Notes")
        self.create_card("Tiny Garden")

    def create_card(self, title):
        card = ctk.CTkFrame(
            self.cards_container,
            corner_radius=20,
            fg_color="#ffffff"
        )
        card.pack(fill="x", pady=10)

        ctk.CTkLabel(
            card,
            text=title,
            font=("SF Pro Rounded", 16, "bold"),
            text_color="#5a4b81"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            card,
            text="(coming next)",
            font=("SF Pro Rounded", 12),
            text_color="#a09ab8"
        ).pack(anchor="w", padx=20, pady=(0, 15))


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app = PetalApp()
    app.mainloop()
