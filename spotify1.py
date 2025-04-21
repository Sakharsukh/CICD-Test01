import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
import random
import threading
import time
from mutagen.mp3 import MP3  # For accurate MP3 duration

class MusicPlayer:
    def __init__(self, root):
        pygame.mixer.init()

        self.root = root
        self.root.title("🎵 My Music Player")
        self.root.geometry("520x700")
        self.root.configure(bg="#2E2E2E")  # Dark theme

        # Initialize player state
        self.songs = []
        self.favorites = set()
        self.playlist = []
        self.current_index = 0
        self.current_song = ""
        self.is_paused = False
        self.keep_playing = False
        self.total_duration = 0

        # Create GUI components
        self.create_buttons()
        self.create_listbox()
        self.create_volume_slider()
        self.create_progress_bar()
        self.create_status_label()

    def select_songs(self):
        # Open file dialog to select songs
        files = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
        if files:
            self.songs = list(files)  # Add selected songs to the song list
            self.update_song_listbox()

    def play_selected_song(self):
        if self.songs:
            # Get the path of the selected song
            selected_index = self.song_listbox.curselection()
            if selected_index:
                self.current_index = selected_index[0]
                self.current_song = self.songs[self.current_index]
                
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play()
                self.is_paused = False
                self.update_status(f"Playing: {os.path.basename(self.current_song)}")
                self.update_progress()

    def pause_resume(self):
        if pygame.mixer.music.get_busy():
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.update_status(f"Resumed: {os.path.basename(self.current_song)}")
            else:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.update_status("Paused")
        else:
            self.update_status("No song is playing")

    def stop(self):
        pygame.mixer.music.stop()
        self.update_status("Stopped")

    def update_song_listbox(self):
        # Update the song listbox with the names of the songs
        self.song_listbox.delete(0, tk.END)
        for song in self.songs:
            self.song_listbox.insert(tk.END, os.path.basename(song))

    def create_buttons(self):
        # Helper to create styled buttons with Unicode symbols for better UI
        def create_btn(symbol, cmd, tooltip=""):
            button = tk.Button(self.root, text=symbol, command=cmd,
                             font=("Segoe UI Emoji", 20), bg="#444", fg="#00FFAA",
                             activebackground="#666", activeforeground="#FFF",
                             bd=0, relief="flat", width=4, height=2)

            # Add tooltip functionality
            if tooltip:
                button.bind("<Enter>", lambda e, t=tooltip: self.show_tooltip(e, t))
                button.bind("<Leave>", self.hide_tooltip)

            return button

        button_frame = tk.Frame(self.root, bg="#2E2E2E")
        button_frame.pack(pady=10)

        # Row 1
        row1 = tk.Frame(button_frame, bg="#2E2E2E")
        row1.pack(pady=4)
        create_btn("📂", self.select_songs, "Select songs").pack(in_=row1, side=tk.LEFT, padx=5)
        create_btn("⭐", self.add_to_favorites, "Add to favorites").pack(in_=row1, side=tk.LEFT, padx=5)
        create_btn("💾", self.save_favorites, "Save favorites").pack(in_=row1, side=tk.LEFT, padx=5)
        create_btn("📥", self.load_favorites, "Load favorites").pack(in_=row1, side=tk.LEFT, padx=5)

        # Row 2
        row2 = tk.Frame(button_frame, bg="#2E2E2E")
        row2.pack(pady=4)
        create_btn("⏮️", self.play_previous, "Play previous").pack(in_=row2, side=tk.LEFT, padx=5)
        create_btn("▶️", self.play_selected_song, "Play selected song").pack(in_=row2, side=tk.LEFT, padx=5)
        create_btn("⏸️", self.pause_resume, "Pause / Resume").pack(in_=row2, side=tk.LEFT, padx=5)
        create_btn("⏹️", self.stop, "Stop").pack(in_=row2, side=tk.LEFT, padx=5)
        create_btn("🔀", self.play_random, "Play random song").pack(in_=row2, side=tk.LEFT, padx=5)

    def create_listbox(self):
        # Listbox for displaying songs
        self.song_listbox = tk.Listbox(self.root, height=10, width=60, bg="#1E1E1E", fg="#00CED1",
                                       selectbackground="#00CED1", selectforeground="#000", font=("Segoe UI", 10))
        self.song_listbox.pack(pady=10)
        self.song_listbox.bind('<<ListboxSelect>>', self.update_selected_indices)

    def create_volume_slider(self):
        # Volume control slider
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Horizontal.TScale", troughcolor="#555", background="#00CED1")

        volume_frame = tk.Frame(self.root, bg="#2E2E2E")
        volume_frame.pack(pady=10)
        tk.Label(volume_frame, text="🔊 Volume", bg="#2E2E2E", fg="#FFF", font=("Segoe UI", 12)).pack()
        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_slider.set(30)
        self.volume_slider.pack()
        pygame.mixer.music.set_volume(0.3)

    def create_progress_bar(self):
        # Song progress bar
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=450, mode='determinate')
        self.progress.pack(pady=(20, 0))
        self.time_label = tk.Label(self.root, text="00:00 / 00:00", bg="#2E2E2E", fg="#FFFFFF",
                                   font=("Segoe UI", 10))
        self.time_label.pack(pady=(0, 10))

    def create_status_label(self):
        # Label to display status messages
        self.label = tk.Label(self.root, text="", wraplength=450, bg="#2E2E2E", fg="#FFA500", font=("Segoe UI", 10, "italic"))
        self.label.pack(pady=10)

    # Tooltip functions
    def show_tooltip(self, event, text):
        self.tooltip = tk.Label(self.root, text=text, bg="#333", fg="#FFF", font=("Segoe UI", 10), padx=5, pady=5)
        self.tooltip.place(x=event.x_root, y=event.y_root)

    def hide_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

    def update_song_listbox(self):
        # Update the song listbox with the names of the songs
        self.song_listbox.delete(0, tk.END)
        for song in self.songs:
            self.song_listbox.insert(tk.END, os.path.basename(song))

    def update_status(self, text):
        # Update status label
        self.label.config(text=text)

    def update_selected_indices(self, event):
        # Update the current song when a song is selected from the listbox
        selected_index = self.song_listbox.curselection()
        if selected_index:
            self.current_index = selected_index[0]
            self.current_song = self.songs[self.current_index]
            self.update_status(f"Selected: {os.path.basename(self.current_song)}")

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume) / 100)

    def play_previous(self):
        pass  # Implement playing the previous song

    def play_random(self):
        if self.songs:
            random_song = random.choice(self.songs)
            self.current_song = random_song
            self.current_index = self.songs.index(random_song)
            pygame.mixer.music.load(random_song)
            pygame.mixer.music.play()
            self.update_status(f"Playing random: {os.path.basename(random_song)}")


if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.mainloop()
