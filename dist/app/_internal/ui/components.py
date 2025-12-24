import customtkinter as ctk
from ui.theme import *


class Card(ctk.CTkFrame):
    """Pixel-style game card with border and shadow effect"""
    def __init__(self, parent, title):
        # Outer frame for pixel border effect
        super().__init__(
            parent,
            fg_color=PIXEL_BORDER,
            corner_radius=0,  # Sharp corners for pixel look
            border_width=0
        )
        
        self.pack(padx=20, pady=12, fill="x")
        
        # Inner padding frame (creates border effect)
        border_frame = ctk.CTkFrame(
            self,
            fg_color=PIXEL_BORDER,
            corner_radius=0
        )
        border_frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Main content frame
        self.content_frame = ctk.CTkFrame(
            border_frame,
            fg_color=CARD_BG,
            corner_radius=0
        )
        self.content_frame.pack(fill="both", expand=True)
        
        # Title with pixel game styling
        title_container = ctk.CTkFrame(
            self.content_frame,
            fg_color=PIXEL_BORDER,
            corner_radius=0,
            height=40
        )
        title_container.pack(fill="x", padx=0, pady=0)
        title_container.pack_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            title_container,
            text=f"▸ {title.upper()}",  # Arrow + uppercase for game feel
            text_color=TITLE_GLOW,
            font=("Pixelify Sans", 16, "bold"),
            anchor="w"
        )
        self.title_label.pack(anchor="w", padx=16, pady=10)
        
    def add_content(self, widget):
        """Helper to add content to the card"""
        widget.pack(in_=self.content_frame)


class PixelButton(ctk.CTkButton):
    """Pixel-style button with game aesthetics"""
    def __init__(self, parent, text, color=BUTTON_PRIMARY, **kwargs):
        super().__init__(
            parent,
            text=text.upper(),  # Uppercase for pixel game style
            fg_color=color,
            hover_color=ACCENT_HOVER if color == BUTTON_PRIMARY else self._darken_color(color),
            text_color=TEXT,
            font=("Pixelify Sans", 13, "bold"),
            corner_radius=0,  # Sharp corners
            border_width=3,
            border_color=PIXEL_BORDER,
            height=40,
            **kwargs
        )
    
    def _darken_color(self, color):
        """Simple color darkening"""
        # Basic implementation - you can make this more sophisticated
        return color


class PixelLabel(ctk.CTkLabel):
    """Pixel-style label for consistent theming"""
    def __init__(self, parent, text, style="normal", **kwargs):
        if style == "title":
            font = ("Pixelify Sans", 18, "bold")
            color = TITLE_GLOW
        elif style == "subtitle":
            font = ("Pixelify Sans", 14)
            color = SUBTEXT
        else:
            font = ("Poppins", 13)
            color = TEXT
            
        super().__init__(
            parent,
            text=text,
            text_color=color,
            font=font,
            **kwargs
        )


class PixelProgressBar(ctk.CTkFrame):
    """Retro pixel-style progress bar"""
    def __init__(self, parent, max_value=100):
        super().__init__(
            parent,
            fg_color=INPUT_BG,
            corner_radius=0,
            border_width=2,
            border_color=PIXEL_BORDER,
            height=24
        )
        
        self.max_value = max_value
        self.current_value = 0
        
        self.progress_fill = ctk.CTkFrame(
            self,
            fg_color=ACCENT_GREEN,
            corner_radius=0,
            width=0,
            height=20
        )
        self.progress_fill.place(x=2, y=2)
        
    def set_value(self, value):
        """Update progress bar value"""
        self.current_value = min(value, self.max_value)
        width = int((self.current_value / self.max_value) * (self.winfo_width() - 4))
        self.progress_fill.configure(width=width)


class PixelInput(ctk.CTkEntry):
    """Pixel-style input field"""
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(
            parent,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            border_width=2,
            corner_radius=0,
            text_color=TEXT,
            placeholder_text=placeholder,
            placeholder_text_color=SUBTEXT,
            font=("Poppins", 13),
            height=38,
            **kwargs
        )
        
        # Bind focus events for glow effect
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        self.configure(border_color=INPUT_FOCUS)
    
    def _on_focus_out(self, event):
        self.configure(border_color=INPUT_BORDER)


class PixelBadge(ctk.CTkFrame):
    """Small badge for stats display (like HP, XP in games)"""
    def __init__(self, parent, icon, value, label=""):
        super().__init__(
            parent,
            fg_color=PIXEL_BORDER,
            corner_radius=0,
            border_width=2,
            border_color=ACCENT_YELLOW
        )
        
        content = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0)
        content.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content,
            text=icon,
            font=("Pixelify Sans", 20),
            text_color=ACCENT_YELLOW
        )
        icon_label.pack(side="left", padx=8, pady=6)
        
        # Value and label
        text_frame = ctk.CTkFrame(content, fg_color="transparent")
        text_frame.pack(side="left", padx=(0, 8))
        
        value_label = ctk.CTkLabel(
            text_frame,
            text=str(value),
            font=("Pixelify Sans", 16, "bold"),
            text_color=TEXT
        )
        value_label.pack()
        
        if label:
            label_label = ctk.CTkLabel(
                text_frame,
                text=label,
                font=("Poppins", 10),
                text_color=SUBTEXT
            )
            label_label.pack()