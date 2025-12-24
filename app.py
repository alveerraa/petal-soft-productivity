import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import json
import pygame
from datetime import date

from ui.theme import *
from ui.components import Card, PixelButton, PixelLabel, PixelInput, PixelBadge


STATE_FILE = "data/state.json"
ctk.set_appearance_mode("dark")  # Dark mode for pixel game aesthetic


# ================= PIXEL TEXT HELPER =================
def pixel_text(text, size, color=TITLE_GLOW):
    font_path = resource_path("assets/fonts/PixelifySans.ttf")
    font = ImageFont.truetype(font_path, size)

    dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    img = Image.new("RGBA", (w + 10, h + 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Pixel glow effect
    draw.text((5, 5), text, font=font, fill=SHADOW_COLOR)  # Shadow
    draw.text((3, 3), text, font=font, fill=color)  # Main text
    
    return ctk.CTkImage(img, size=(w + 4, h + 4))


class PetalApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("650x980")
        self.title("🌸 PetalOS")
        self.configure(fg_color=BG)

        # ---------- FONTS ----------
        self.TITLE_FONT = ctk.CTkFont(family="Pixelify Sans", size=32, weight="bold")
        self.BODY_FONT = ctk.CTkFont(family="Poppins", size=13)
        self.SMALL_FONT = ctk.CTkFont(family="Poppins", size=11)
        self.PIXEL_FONT = ctk.CTkFont(family="Pixelify Sans", size=14)

        # ---------- MUSIC ----------
        pygame.mixer.init()
        self.music_on = True
        try:
            pygame.mixer.music.load("assets/music/cutie-japan-lofi-402355.mp3")
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(-1)
        except:
            pass

        # ---------- TIMER ----------
        self.remaining = 0
        self.current_duration = 0
        self.timer_running = False
        self.timer_paused = False
        self.timer_after_id = None

        # ---------- DATA ----------
        self.state = self.load_state()
        self.images = self.load_images()

        # ---------- UI ----------
        self.build_ui()
        self.refresh_garden()

    # ================= ANIMATIONS =================
    def pop_widget(self, widget):
        try:
            original_fg = widget.cget("fg_color")
            widget.configure(fg_color=ACCENT_HOVER)
            self.after(150, lambda: widget.configure(fg_color=original_fg))
        except:
            pass
    
    def glow_widget(self, widget):
        try:
            widget.configure(text_color=ACCENT_YELLOW)
            self.after(300, lambda: widget.configure(text_color=TEXT))
        except:
            pass

    # ================= MUSIC =================
    def toggle_music(self):
        if self.music_on:
            pygame.mixer.music.pause()
            self.music_btn.configure(text="🔇")
        else:
            pygame.mixer.music.unpause()
            self.music_btn.configure(text="🔊")
        self.music_on = not self.music_on

    # ================= STATE =================
    def load_state(self):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            # Default state
            return {
                "today_sessions": 0,
                "streak": 0,
                "mood": "",
                "notes": "",
                "main_task": "",
                "task_done": False,
                "plants": {"rose": 0, "hydrangea": 0, "sunflower": 0},
                "history": [],
                "last_active_date": ""
            }

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def update_streak(self):
        today = str(date.today())
        if self.state["today_sessions"] > 0:
            if self.state.get("last_active_date") != today:
                self.state["streak"] = self.state.get("streak", 0) + 1
                self.state["last_active_date"] = today
                self.show_toast(f"🔥 STREAK: {self.state['streak']} DAYS!", SUCCESS)
        self.save_state()
        self.update_stats_bar()

    # ================= IMAGES =================

    def img(self, path, size):
        """Load an image with error handling."""
        try:
            full_path = resource_path(path)
            return ctk.CTkImage(
                Image.open(full_path),
                size=size
            )
        except FileNotFoundError:
            print(f"[IMG NOT FOUND] {path}")
            return None
        except Exception as e:
            print(f"[IMG LOAD FAILED] {path} -> {e}")
            return None

    def load_images(self):
        """Load all application images."""
        imgs = {
            "moods": {},
            "plants": {},
            "ui": {}  # You can add UI images here if needed
        }

        # Load mood icons
        mood_names = ["sleepy", "motivated", "angry", "sad"]
        for mood in mood_names:
            img = self.img(f"assets/icons/{mood}.png", (48, 48))
            if img:
                imgs["moods"][mood.capitalize()] = img
            else:
                # Create a placeholder or use default
                print(f"Warning: Could not load mood icon for {mood}")

        # Load plant images
        plant_types = ["rose", "hydrangea", "sunflower"]
        growth_stages = ["seed", "grow", "bloom"]

        for plant in plant_types:
            imgs["plants"][plant] = {}
            for stage in growth_stages:
                img_path = f"assets/plants/{plant}_{stage}.png"
                img = self.img(img_path, (64, 64))
                if img:
                    imgs["plants"][plant][stage] = img
                else:
                    print(f"Warning: Could not load {plant} {stage} image")
                    imgs["plants"][plant][stage] = None  # Explicitly set to None

        return imgs

    
    
    # ================= PROGRESS FLOWER =================
    def progress_flower_card(self, parent):
        card = Card(parent, "Today's Growth")
        
        content = ctk.CTkFrame(card.content_frame, fg_color="transparent")
        content.pack(pady=20, fill="x")

        self.progress_flower_label = ctk.CTkLabel(content, text="")
        self.progress_flower_label.pack(pady=10)
        
        self.progress_text = PixelLabel(
            content, 
            "PLANT A SEED", 
            style="subtitle"
        )
        self.progress_text.pack(pady=5)

        self.update_progress_flower()

    def update_progress_flower(self):
        sessions = self.state["today_sessions"]

        if sessions == 0:
            img = self.images["plants"]["rose"]["seed"]
            text = "PLANT A SEED"
            color = SUBTEXT
        elif sessions == 1:
            img = self.images["plants"]["rose"]["grow"]
            text = "GROWING... 🌱"
            color = ACCENT_GREEN
        else:
            img = self.images["plants"]["rose"]["bloom"]
            text = "BLOOMING! 🌸"
            color = SUCCESS

        if img:
            self.progress_flower_label.configure(image=img)
        self.progress_text.configure(text=text, text_color=color)
        self.glow_widget(self.progress_text)

    # ================= UI =================
    def build_ui(self):
        # Main scrollable container
        self.scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color=BG,
            scrollbar_button_color=PIXEL_BORDER,
            scrollbar_button_hover_color=ACCENT
        )
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== HEADER =====
        header = ctk.CTkFrame(self.scroll, fg_color=CARD_BG, corner_radius=0, border_width=3, border_color=PIXEL_BORDER)
        header.pack(fill="x", pady=(0, 15), padx=5)
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(fill="x", pady=20)

        # Pixel title with glow
        title_label = ctk.CTkLabel(
            title_frame,
            text="",
            image=pixel_text("⚡ PETALOS ⚡", 36, ACCENT)
        )
        title_label.pack()

        # Subtitle
        PixelLabel(
            title_frame,
            "FOCUS • FEEL • GROW",
            style="subtitle"
        ).pack(pady=5)

        # Stats bar
        self.stats_bar(header)

        # Control buttons row
        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(pady=(10, 20))
        
        self.music_btn = ctk.CTkLabel(
            controls, 
            text="🔊", 
            cursor="hand2",
            font=("Pixelify Sans", 24),
            text_color=ACCENT_YELLOW
        )
        self.music_btn.pack(side="left", padx=15)
        self.music_btn.bind("<Button-1>", lambda e: self.toggle_music())

        history_btn = ctk.CTkLabel(
            controls, 
            text="📖", 
            cursor="hand2",
            font=("Pixelify Sans", 24),
            text_color=ACCENT_BLUE
        )
        history_btn.pack(side="left", padx=15)
        history_btn.bind("<Button-1>", lambda e: self.show_history())
        
        reset_btn = ctk.CTkLabel(
            controls, 
            text="🔄", 
            cursor="hand2",
            font=("Pixelify Sans", 24),
            text_color=ERROR
        )
        reset_btn.pack(side="left", padx=15)
        reset_btn.bind("<Button-1>", lambda e: self.reset_today())

        # Main content
        self.main_task_card(self.scroll)
        self.focus_card(self.scroll)
        self.progress_flower_card(self.scroll)
        self.mood_card(self.scroll)
        self.notes_card(self.scroll)
        self.garden_card(self.scroll)
        self.end_day_card(self.scroll)

    # ================= STATS BAR =================
    def stats_bar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=10)
        
        self.session_badge = PixelBadge(bar, "⚡", self.state["today_sessions"], "SESSIONS")
        self.session_badge.pack(side="left", padx=10)
        
        self.streak_badge = PixelBadge(bar, "🔥", self.state.get("streak", 0), "STREAK")
        self.streak_badge.pack(side="right", padx=10)
    
    def update_stats_bar(self):
        # Update badges with current values
        for widget in self.session_badge.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for label in child.winfo_children():
                        if isinstance(label, ctk.CTkLabel) and label.cget("font")[1] == 16:
                            label.configure(text=str(self.state["today_sessions"]))
        
        for widget in self.streak_badge.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for label in child.winfo_children():
                        if isinstance(label, ctk.CTkLabel) and label.cget("font")[1] == 16:
                            label.configure(text=str(self.state.get("streak", 0)))

    # ================= MAIN TASK =================
    def main_task_card(self, parent):
        card = Card(parent, "Main Quest")

        content = ctk.CTkFrame(card.content_frame, fg_color="transparent")
        content.pack(padx=20, pady=15, fill="x")

        self.task_done_var = ctk.BooleanVar(value=self.state["task_done"])

        checkbox_frame = ctk.CTkFrame(content, fg_color="transparent")
        checkbox_frame.pack(fill="x")

        ctk.CTkCheckBox(
            checkbox_frame,
            text="",
            variable=self.task_done_var,
            command=self.toggle_task_done,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            border_color=PIXEL_BORDER,
            corner_radius=0,
            border_width=2
        ).pack(side="left", padx=10)

        self.task_entry = PixelInput(checkbox_frame, placeholder="What's your main quest today?")
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.task_entry.insert(0, self.state["main_task"])

    def toggle_task_done(self):
        if self.task_done_var.get():
            self.show_toast("⚔️ QUEST COMPLETE!", SUCCESS)
            self.task_entry.delete(0, "end")
            self.task_done_var.set(False)
            self.state["main_task"] = ""
            self.save_state()

    # ================= TIMER =================
    def focus_card(self, parent):
        card = Card(parent, "Focus Chamber")

        content = ctk.CTkFrame(card.content_frame, fg_color="transparent")
        content.pack(pady=20)

        # Timer display with pixel border
        timer_frame = ctk.CTkFrame(
            content,
            fg_color=PIXEL_BORDER,
            corner_radius=0,
            border_width=0
        )
        timer_frame.pack(pady=10)
        
        timer_inner = ctk.CTkFrame(
            timer_frame,
            fg_color=INPUT_BG,
            corner_radius=0
        )
        timer_inner.pack(padx=4, pady=4)

        self.timer_label = ctk.CTkLabel(
            timer_inner,
            text="00:00",
            font=("Pixelify Sans", 48, "bold"),
            text_color=ACCENT_GREEN,
            width=200,
            height=80
        )
        self.timer_label.pack(padx=30, pady=20)

        # Duration buttons
        btns = ctk.CTkFrame(content, fg_color="transparent")
        btns.pack(pady=15)

        for i, mins in enumerate([15, 25, 35]):
            colors = [BUTTON_SECONDARY, BUTTON_PRIMARY, ACCENT_PURPLE]
            PixelButton(
                btns,
                text=f"{mins} MIN",
                color=colors[i],
                command=lambda m=mins: self.start_timer(m)
            ).pack(side="left", padx=8)

        # Control links
        links = ctk.CTkFrame(content, fg_color="transparent")
        links.pack(pady=10)

        self.pause_link = ctk.CTkLabel(
            links,
            text="⏸ PAUSE",
            cursor="hand2",
            text_color=SUBTEXT,
            font=self.PIXEL_FONT
        )
        self.pause_link.pack(side="left", padx=20)
        self.pause_link.bind("<Button-1>", lambda e: self.toggle_pause())

        restart_link = ctk.CTkLabel(
            links,
            text="🔄 RESTART",
            cursor="hand2",
            text_color=SUBTEXT,
            font=self.PIXEL_FONT
        )
        restart_link.pack(side="left", padx=20)
        restart_link.bind("<Button-1>", lambda e: self.restart_timer())

    def start_timer(self, minutes):
        self.stop_timer()
        self.current_duration = minutes
        self.remaining = minutes * 60
        self.timer_running = True
        self.timer_paused = False
        self.timer_label.configure(text_color=ACCENT_GREEN)
        self.update_timer()

    def update_timer(self):
        if not self.timer_running:
            return
        if not self.timer_paused:
            mins, secs = divmod(self.remaining, 60)
            self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
            
            # Color changes based on time
            if self.remaining < 60:
                self.timer_label.configure(text_color=ERROR)
            elif self.remaining < 300:
                self.timer_label.configure(text_color=WARNING)
            
            self.remaining -= 1
            if self.remaining < 0:
                self.complete_focus()
                return
        self.timer_after_id = self.after(1000, self.update_timer)

    def toggle_pause(self):
        self.timer_paused = not self.timer_paused
        self.pause_link.configure(
            text="▶ RESUME" if self.timer_paused else "⏸ PAUSE"
        )

    def restart_timer(self):
        if self.current_duration:
            self.start_timer(self.current_duration)

    def stop_timer(self):
        self.timer_running = False
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None

    def complete_focus(self):
        self.stop_timer()
        self.timer_label.configure(text="DONE!", text_color=SUCCESS)
        self.state["today_sessions"] += 1
        self.grow_garden()
        self.save_state()
        self.refresh_garden()
        self.update_progress_flower()
        self.update_stats_bar()
        self.show_toast("⚡ +1 SESSION! GARDEN GREW!", SUCCESS)

    # ================= MOOD =================
    def mood_card(self, parent):
        card = Card(parent, "Energy Check")
        
        content = ctk.CTkFrame(card.content_frame, fg_color="transparent")
        content.pack(pady=20)
        
        grid = ctk.CTkFrame(content, fg_color="transparent")
        grid.pack()

        for i, (mood, img) in enumerate(self.images["moods"].items()):
            if img:
                btn_frame = ctk.CTkFrame(
                    grid,
                    fg_color=PIXEL_BORDER,
                    corner_radius=0,
                    border_width=2,
                    border_color=PIXEL_BORDER
                )
                btn_frame.grid(row=i // 2, column=i % 2, padx=15, pady=15)
                
                btn = ctk.CTkButton(
                    btn_frame,
                    image=img,
                    text=mood.upper(),
                    compound="top",
                    fg_color=CARD_BG,
                    hover_color=INPUT_BG,
                    text_color=TEXT,
                    font=self.PIXEL_FONT,
                    corner_radius=0,
                    border_width=0,
                    width=140,
                    height=120
                )
                btn.pack(padx=3, pady=3)
                btn.configure(command=lambda m=mood, b=btn_frame: (
                    self.pop_widget(b), self.set_mood(m)
                ))

        self.mood_reaction = PixelLabel(
            content,
            "",
            style="subtitle"
        )
        self.mood_reaction.pack(pady=15)

    def set_mood(self, mood):
        self.state["mood"] = mood
        self.save_state()
        reactions = {
            "Sleepy": "☁️ START GENTLY",
            "Motivated": "🌱 HARNESS THIS ENERGY",
            "Angry": "🔥 CHANNEL IT INTO FOCUS",
            "Sad": "🤍 BE KIND TO YOURSELF"
        }
        self.mood_reaction.configure(text=reactions[mood])

    # ================= NOTES =================
    def notes_card(self, parent):
        card = Card(parent, "Field Notes")

        content = ctk.CTkFrame(card.content_frame, fg_color="transparent")
        content.pack(padx=20, pady=15, fill="x")

        # Notes textbox with pixel border
        notes_frame = ctk.CTkFrame(content, fg_color=PIXEL_BORDER, corner_radius=0)
        notes_frame.pack(fill="x", pady=(0, 15))
        
        self.notes = ctk.CTkTextbox(
            notes_frame,
            height=120,
            font=self.BODY_FONT,
            fg_color=INPUT_BG,
            border_width=0,
            corner_radius=0,
            text_color=TEXT
        )
        self.notes.pack(padx=3, pady=3, fill="x")
        self.notes.insert("1.0", self.state["notes"])

        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack()

        PixelButton(
            btn_row,
            text="💾 SAVE",
            color=BUTTON_SUCCESS,
            command=self.save_notes
        ).pack(side="left", padx=8)

        PixelButton(
            btn_row,
            text="🗑 CLEAR",
            color=BUTTON_DANGER,
            command=self.delete_notes
        ).pack(side="left", padx=8)

    def save_notes(self):
        self.state["notes"] = self.notes.get("1.0", "end").strip()
        self.state["main_task"] = self.task_entry.get()
        self.save_state()
        self.show_toast("💾 NOTES SAVED", INFO)

    def delete_notes(self):
        self.state["notes"] = ""
        self.save_state()
        self.notes.delete("1.0", "end")
        self.show_toast("🗑 NOTES CLEARED", WARNING)

    # ================= GARDEN =================
    def garden_card(self, parent):
        card = Card(parent, "Pixel Garden")
        
        content = ctk.CTkFrame(card.content_frame, fg_color="transparent")
        content.pack(pady=20)
        
        self.garden = ctk.CTkFrame(content, fg_color=INPUT_BG, corner_radius=0, border_width=3, border_color=PIXEL_BORDER)
        self.garden.pack(padx=20, pady=10)

        self.plant_labels = {}
        plants_frame = ctk.CTkFrame(self.garden, fg_color="transparent")
        plants_frame.pack(pady=20)
        
        for plant in self.state["plants"]:
            lbl = ctk.CTkLabel(plants_frame, text="")
            lbl.pack(side="left", padx=25)
            self.plant_labels[plant] = lbl

    def grow_garden(self):
        for plant in self.state["plants"]:
            if self.state["plants"][plant] < 2:
                self.state["plants"][plant] += 1
                break

    def refresh_garden(self):
        for plant, stage in self.state["plants"].items():
            key = ["seed", "grow", "bloom"][stage]
            img = self.images["plants"][plant][key]
            if img:
                lbl = self.plant_labels[plant]
                lbl.configure(image=img)
                self.pop_widget(lbl)

    # ================= SAVE / RESET / HISTORY =================
    def save_today(self):
        snapshot = {
            "sessions": self.state["today_sessions"],
            "mood": self.state["mood"],
            "notes": self.state["notes"],
            "task": self.state["main_task"],
            "plants": self.state["plants"].copy()
        }
        self.state["history"].append(snapshot)
        self.reset_today(False)
        self.save_state()
        self.update_progress_flower()
        self.show_toast("💾 DAY SAVED TO HISTORY", SUCCESS)

    def reset_today(self, show=True):
        self.stop_timer()
        self.timer_label.configure(text="00:00", text_color=ACCENT_GREEN)

        self.state["today_sessions"] = 0
        self.state["mood"] = ""
        self.state["notes"] = ""
        self.state["main_task"] = ""
        self.state["task_done"] = False

        self.task_entry.delete(0, "end")
        self.task_done_var.set(False)
        self.notes.delete("1.0", "end")

        for p in self.state["plants"]:
            self.state["plants"][p] = 0

        self.save_state()
        self.refresh_garden()
        self.update_progress_flower()
        self.update_stats_bar()

        if show:
            self.show_toast("🔄 FRESH START", INFO)

    def show_history(self):
        win = ctk.CTkToplevel(self)
        win.title("📖 History Log")
        win.geometry("450x550")
        win.configure(fg_color=BG)

        # Header
        header = ctk.CTkFrame(win, fg_color=CARD_BG, corner_radius=0, border_width=3, border_color=PIXEL_BORDER)
        header.pack(fill="x", padx=15, pady=15)
        
        PixelLabel(header, "📖 QUEST LOG", style="title").pack(pady=20)

        frame = ctk.CTkScrollableFrame(win, fg_color=BG)
        frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        if not self.state["history"]:
            PixelLabel(frame, "NO ENTRIES YET 🌸", style="subtitle").pack(pady=40)
            return

        for i, day in enumerate(self.state["history"], 1):
            day_card = ctk.CTkFrame(frame, fg_color=CARD_BG, corner_radius=0, border_width=2, border_color=PIXEL_BORDER)
            day_card.pack(fill="x", pady=8)
            
            day_content = ctk.CTkFrame(day_card, fg_color="transparent")
            day_content.pack(padx=15, pady=15, fill="x")
            
            PixelLabel(day_content, f"▸ DAY {i}", style="title").pack(anchor="w")
            
            info_text = f"""⚡ {day['sessions']} sessions
🎭 Mood: {day['mood'] or 'Not set'}
⚔️ Quest: {day['task'] or 'None'}
📝 {day['notes'][:50]}{'...' if len(day['notes']) > 50 else ''}"""
            
            ctk.CTkLabel(
                day_content,
                text=info_text,
                justify="left",
                text_color=TEXT,
                font=self.BODY_FONT
            ).pack(anchor="w", pady=(10, 0))

    # ================= END DAY =================
    def end_day_card(self, parent):
        card = Card(parent, "Day's End")
        
        content = ctk.CTkFrame(card.content_frame, fg_color="transparent")
        content.pack(pady=20)
        
        PixelButton(
            content,
            text="🌙 END DAY & SAVE",
            color=ACCENT_PURPLE,
            command=self.end_day,
            width=250
        ).pack()

    def end_day(self):
        self.stop_timer()
        self.timer_label.configure(text="00:00", text_color=ACCENT_GREEN)
        self.save_today()
        self.update_streak()
        self.show_popup("🌙 REST WELL", "You showed up today. That's what matters. 🌸")

    # ================= HELPERS =================
    def show_toast(self, text, color=ACCENT):
        toast_frame = ctk.CTkFrame(
            self,
            fg_color=PIXEL_BORDER,
            corner_radius=0,
            border_width=3,
            border_color=color
        )
        toast_frame.place(relx=0.5, rely=0.92, anchor="center")
        
        toast_inner = ctk.CTkFrame(toast_frame, fg_color=CARD_BG, corner_radius=0)
        toast_inner.pack(padx=3, pady=3)
        
        toast = ctk.CTkLabel(
            toast_inner,
            text=text,
            font=self.PIXEL_FONT,
            text_color=color
        )
        toast.pack(padx=25, pady=12)
        
        self.after(2000, toast_frame.destroy)

    def show_popup(self, title, text):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("420x280")
        win.configure(fg_color=BG)
        
        content = ctk.CTkFrame(
            win,
            fg_color=CARD_BG,
            corner_radius=0,
            border_width=4,
            border_color=ACCENT
        )
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        PixelLabel(content, title, style="title").pack(pady=(30, 20))
        
        ctk.CTkLabel(
            content,
            text=text,
            font=self.BODY_FONT,
            justify="center",
            wraplength=340,
            text_color=TEXT
        ).pack(padx=30, pady=(0, 20))
        
        PixelButton(
            content,
            text="OK",
            color=ACCENT,
            command=win.destroy
        ).pack(pady=(10, 30))

    def soft_pulse(self, widget):
        try:
            widget.configure(text_color=ACCENT_YELLOW)
            self.after(200, lambda: widget.configure(text_color=TEXT))
        except:
            pass


if __name__ == "__main__":
    app = PetalApp()
    app.mainloop()