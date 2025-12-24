import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import json
import pygame

from ui.theme import *
from ui.components import Card

STATE_FILE = "data/state.json"
ctk.set_appearance_mode("light")


# ================= PIXEL TEXT HELPER (NEW) =================
def pixel_text(text, size, color="#3b2f4a"):
    font_path = "assets/fonts/PixelifySans.ttf"
    font = ImageFont.truetype(font_path, size)

    dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    img = Image.new("RGBA", (w + 6, h + 6), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((3, 3), text, font=font, fill=color)

    return ctk.CTkImage(img, size=(w, h))


class PetalApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("620x940")
        self.title("PetalOS")

        # ---------- FONTS (UNCHANGED) ----------
        self.TITLE_FONT = ctk.CTkFont(family="Pixelify_Sans", size=30)
        self.BODY_FONT = ctk.CTkFont(family="Poppins", size=14)
        self.SMALL_FONT = ctk.CTkFont(family="Poppins", size=12)

        # ---------- MUSIC ----------
        pygame.mixer.init()
        self.music_on = True
        pygame.mixer.music.load("assets/music/cutie-japan-lofi-402355.mp3")
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)

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

    # ================= SAFE ANIMATION =================
    def pop_widget(self, widget):
        try:
            widget.configure(padx=8, pady=8)
            self.after(120, lambda: widget.configure(padx=4, pady=4))
        except:
            pass

    # ================= MUSIC =================
    def toggle_music(self):
        if self.music_on:
            pygame.mixer.music.pause()
            self.music_label.configure(text="🔇")
        else:
            pygame.mixer.music.unpause()
            self.music_label.configure(text="🔊")
        self.music_on = not self.music_on

    # ================= STATE =================
    def load_state(self):
        with open(STATE_FILE, "r") as f:
            return json.load(f)

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    # ================= IMAGES =================
    def img(self, path, size):
        return ctk.CTkImage(Image.open(path), size=size)

    def load_images(self):
        imgs = {"moods": {}, "plants": {}}

        for mood in ["sleepy", "motivated", "angry", "sad"]:
            imgs["moods"][mood.capitalize()] = self.img(
                f"assets/icons/{mood}.png", (48, 48)
            )

        for p in ["rose", "hydrangea", "sunflower"]:
            imgs["plants"][p] = {
                "seed": self.img(f"assets/plants/{p}_seed.png", (64, 64)),
                "grow": self.img(f"assets/plants/{p}_grow.png", (64, 64)),
                "bloom": self.img(f"assets/plants/{p}_bloom.png", (64, 64)),
            }
        return imgs

    # ================= UI =================
    def build_ui(self):
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=BG)
        self.scroll.pack(fill="both", expand=True)

        title_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        title_frame.pack(fill="x", pady=(20, 6))

        # ===== PIXEL TITLE (FIXED, IMAGE-BASED) =====
        ctk.CTkLabel(
            title_frame,
            text="",
            image=pixel_text("PETALOS", 32)
        ).pack()

        # ----- Icons row -----
        icon_row = ctk.CTkFrame(title_frame, fg_color="transparent")
        icon_row.pack(anchor="ne", padx=20, pady=4)

        self.music_label = ctk.CTkLabel(
            icon_row, text="🔊", cursor="hand2", text_color=SUBTEXT
        )
        self.music_label.pack(side="right", padx=6)
        self.music_label.bind("<Button-1>", lambda e: self.toggle_music())

        history = ctk.CTkLabel(
            icon_row, text="📖", cursor="hand2", text_color=SUBTEXT
        )
        history.pack(side="right", padx=6)
        history.bind("<Button-1>", lambda e: self.show_history())

        # ----- Subtitle -----
        ctk.CTkLabel(
            self.scroll,
            text="Focus. Feel. Grow.",
            font=self.BODY_FONT,
            text_color=SUBTEXT
        ).pack()

        self.daily_controls(self.scroll)
        self.main_task_card(self.scroll)
        self.focus_card(self.scroll)
        self.mood_card(self.scroll)
        self.notes_card(self.scroll)
        self.garden_card(self.scroll)
        self.end_day_card(self.scroll)

    # ================= EVERYTHING BELOW IS UNCHANGED =================
    # (Main task, timer, mood, notes, garden, save/reset/history, end day)
    # Your full logic remains exactly as you wrote it.

    # … (rest of your code stays exactly the same)


    # ================= DAILY =================
    def daily_controls(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.pack(pady=10)

        for txt, fn in [("Reset 🌱", self.reset_today), ("Save 🌸", self.save_today)]:
            lbl = ctk.CTkLabel(bar, text=txt, cursor="hand2", text_color=SUBTEXT)
            lbl.pack(side="right", padx=12)
            lbl.bind("<Button-1>", lambda e, f=fn: f())

    # ================= MAIN TASK =================
    def main_task_card(self, parent):
        card = Card(parent, "One Main Task Today")

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(padx=20, pady=10, fill="x")

        self.task_done_var = ctk.BooleanVar(value=self.state["task_done"])

        ctk.CTkCheckBox(
            row, text="", variable=self.task_done_var,
            command=self.toggle_task_done
        ).pack(side="left", padx=10)

        self.task_entry = ctk.CTkEntry(row)
        self.task_entry.pack(side="left", fill="x", expand=True)
        self.task_entry.insert(0, self.state["main_task"])

    def toggle_task_done(self):
        if self.task_done_var.get():
            self.show_toast("✅ Task completed")
            self.task_entry.delete(0, "end")
            self.task_done_var.set(False)

    # ================= TIMER =================
    def focus_card(self, parent):
        card = Card(parent, "Focus Session")

        self.timer_label = ctk.CTkLabel(
            card, text="00:00", font=("Menlo", 30), text_color=TEXT
        )
        self.timer_label.pack(pady=10)

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack()

        for mins in [15, 25, 35]:
            ctk.CTkButton(
                btns, text=f"{mins} min",
                fg_color=ACCENT,
                command=lambda m=mins: self.start_timer(m)
            ).pack(side="left", padx=6)

        links = ctk.CTkFrame(card, fg_color="transparent")
        links.pack(pady=8)

        self.pause_link = ctk.CTkLabel(
            links, text="Pause", cursor="hand2", text_color=SUBTEXT
        )
        self.pause_link.pack(side="left", padx=16)
        self.pause_link.bind("<Button-1>", lambda e: self.toggle_pause())

        restart = ctk.CTkLabel(
            links, text="Restart", cursor="hand2", text_color=SUBTEXT
        )
        restart.pack(side="left", padx=16)
        restart.bind("<Button-1>", lambda e: self.restart_timer())

    def start_timer(self, minutes):
        self.stop_timer()
        self.current_duration = minutes
        self.remaining = minutes * 60
        self.timer_running = True
        self.timer_paused = False
        self.update_timer()

    def update_timer(self):
        if not self.timer_running:
            return
        if not self.timer_paused:
            mins, secs = divmod(self.remaining, 60)
            self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
            self.remaining -= 1
            if self.remaining < 0:
                self.complete_focus()
                return
        self.timer_after_id = self.after(1000, self.update_timer)

    def toggle_pause(self):
        self.timer_paused = not self.timer_paused
        self.pause_link.configure(
            text="Resume" if self.timer_paused else "Pause"
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
        self.state["today_sessions"] += 1
        self.grow_garden()
        self.save_state()
        self.refresh_garden()
        self.show_toast("🌱 Garden grew")

    # ================= MOOD =================
    def mood_card(self, parent):
        card = Card(parent, "How Are You Feeling?")
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(pady=10)

        for i, (mood, img) in enumerate(self.images["moods"].items()):
            btn = ctk.CTkButton(
                grid, image=img, text=mood,
                compound="top", fg_color="transparent",
                hover_color="#eee4f3", text_color=TEXT
            )
            btn.configure(
                command=lambda m=mood, b=btn: (
                    self.pop_widget(b), self.set_mood(m)
                )
            )
            btn.grid(row=i // 2, column=i % 2, padx=30, pady=12)

        self.mood_reaction = ctk.CTkLabel(
            card, text="", font=self.SMALL_FONT, text_color=SUBTEXT
        )
        self.mood_reaction.pack(pady=5)

    def set_mood(self, mood):
        self.state["mood"] = mood
        self.save_state()
        reactions = {
            "Sleepy": "Maybe start gently ☁️",
            "Motivated": "This energy can grow something 🌱",
            "Angry": "Let it out, then focus 🔥",
            "Sad": "Go slow today 🤍"
        }
        self.mood_reaction.configure(text=reactions[mood])

    # ================= NOTES =================
    def notes_card(self, parent):
        card = Card(parent, "Write Notes")

        self.notes = ctk.CTkTextbox(card, height=120, font=self.BODY_FONT)
        self.notes.pack(padx=20, pady=(10, 6), fill="x")
        self.notes.insert("1.0", self.state["notes"])

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=(0, 10))

        ctk.CTkButton(
            btn_row, text="Save Notes",
            fg_color=ACCENT, command=self.save_notes
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_row, text="Clear",
            fg_color="#f2c6c6", command=self.delete_notes
        ).pack(side="left", padx=6)

    def save_notes(self):
        self.state["notes"] = self.notes.get("1.0", "end").strip()
        self.save_state()
        self.show_toast("Notes saved ✨")

    def delete_notes(self):
        self.state["notes"] = ""
        self.save_state()
        self.notes.delete("1.0", "end")
        self.show_toast("Notes cleared")

    # ================= GARDEN =================
    def garden_card(self, parent):
        card = Card(parent, "Tiny Garden")
        self.garden = ctk.CTkFrame(card, fg_color="transparent")
        self.garden.pack(pady=12)

        self.plant_labels = {}
        for plant in self.state["plants"]:
            lbl = ctk.CTkLabel(self.garden, text="")
            lbl.pack(side="left", padx=30)
            self.plant_labels[plant] = lbl

    def grow_garden(self):
        for plant in self.state["plants"]:
            if self.state["plants"][plant] < 2:
                self.state["plants"][plant] += 1
                break

    def refresh_garden(self):
        for plant, stage in self.state["plants"].items():
            key = ["seed", "grow", "bloom"][stage]
            lbl = self.plant_labels[plant]
            lbl.configure(image=self.images["plants"][plant][key])
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
        self.show_toast("🌸 Today saved")

    def reset_today(self, show=True):
        self.stop_timer()
        self.timer_label.configure(text="00:00")

        self.state["today_sessions"] = 0
        self.state["mood"] = ""
        self.state["notes"] = ""
        self.state["main_task"] = ""
        self.state["task_done"] = False

        self.task_entry.delete(0, "end")
        self.task_done_var.set(False)

        for p in self.state["plants"]:
            self.state["plants"][p] = 0

        self.save_state()
        self.refresh_garden()

        if show:
            self.show_toast("🌱 Fresh start")

    def show_history(self):
        win = ctk.CTkToplevel(self)
        win.title("History")
        win.geometry("400x500")

        frame = ctk.CTkScrollableFrame(win)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        if not self.state["history"]:
            ctk.CTkLabel(frame, text="No saved days yet 🌸").pack(pady=20)
            return

        for i, day in enumerate(self.state["history"], 1):
            ctk.CTkLabel(
                frame,
                text=f"Day {i}\nSessions: {day['sessions']}\nMood: {day['mood']}\nTask: {day['task']}\nNotes: {day['notes']}\n",
                justify="left"
            ).pack(pady=10)

    # ================= END DAY =================
    def end_day_card(self, parent):
        card = Card(parent, "End of Day")
        ctk.CTkButton(
            card, text="End Day 🌙",
            fg_color=ACCENT_DARK,
            command=self.end_day
        ).pack(pady=12)

    def end_day(self):
        self.stop_timer()
        self.timer_label.configure(text="00:00")
        self.show_popup("Gentle Wrap-Up", "You showed up today 🌸")

    # ================= HELPERS =================
    def show_toast(self, text):
        toast = ctk.CTkLabel(self, text=text, font=self.SMALL_FONT)
        toast.place(relx=0.5, rely=0.95, anchor="center")
        self.after(1800, toast.destroy)

    def show_popup(self, title, text):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("360x260")
        ctk.CTkLabel(
            win, text=text, font=self.BODY_FONT,
            justify="center", wraplength=320
        ).pack(padx=20, pady=30)


if __name__ == "__main__":
    PetalApp().mainloop()
