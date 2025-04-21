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
        self.root.title("Simple Music Player")
        self.root.geometry("500x650")
        self.root.configure(bg="#808080")

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

    def create_buttons(self):
        # Helper to create styled buttons
        def create_btn(text, cmd):
            return tk.Button(self.root, text=text, command=cmd, bg="#333", fg="#fff", width=25)

        # Action buttons
        create_btn("Select Songs", self.select_songs).pack(pady=5)
        create_btn("Play Random", self.play_random).pack(pady=5)
        create_btn("Previous", self.play_previous).pack(pady=5)
        create_btn("Next", self.play_next).pack(pady=5)
        create_btn("Pause / Resume", self.pause_resume).pack(pady=5)
        create_btn("Stop", self.stop).pack(pady=5)
        create_btn("Add to Favorites", self.add_to_favorites).pack(pady=5)
        create_btn("Save Favorites", self.save_favorites).pack(pady=5)
        create_btn("Load Favorites", self.load_favorites).pack(pady=5)

        # Button to play selected song
        play_btn = tk.Button(self.root, text="Play Selected", command=self.play_selected_song, bg="#333", fg="#4169E1", width=25)
        play_btn.pack(pady=5)

    def create_listbox(self):
        # Listbox for songs
        self.song_listbox = tk.Listbox(self.root, height=8, width=50, bg="#333", fg="#4169E1", selectbackground="gray", selectmode=tk.MULTIPLE)
        self.song_listbox.pack(pady=10)
        self.song_listbox.bind('<<ListboxSelect>>', self.update_selected_indices)

    def create_volume_slider(self):
        # Volume control slider
        self.volume_slider = tk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, label="Volume",
                                      command=self.set_volume, bg="#808080", fg="#FFFFFF", highlightbackground="#808080", troughcolor="#00008B")
        self.volume_slider.set(30)
        self.volume_slider.pack(pady=10)
        pygame.mixer.music.set_volume(0.7)

    def create_progress_bar(self):
        # Song progress bar
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=350, mode='determinate')
        self.progress.pack(pady=(10, 0))
        self.time_label = tk.Label(self.root, text="00:00 / 00:00", bg="#808080", fg="#FFFFFF")
        self.time_label.pack(pady=(0, 10))

    def create_status_label(self):
        # Label to display status messages
        self.label = tk.Label(self.root, text="", wraplength=450, bg="#808080", fg="#FFFFFF")
        self.label.pack(pady=10)

    def update_song_list(self):
        # Update listbox display with song names and highlight favorites with a star
        self.song_listbox.delete(0, tk.END)
        for song in self.songs:
            name = os.path.basename(song)
            if song in self.favorites:
                name = "★ " + name  # Add a star symbol for favorites
            self.song_listbox.insert(tk.END, name)
        self.label.config(text=f"{len(self.songs)} songs loaded.")

    def select_songs(self):
        # Select songs to load into the player
        files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        self.songs = list(files)
        self.update_song_list()

    def play_random(self):
        # Start playing random songs continuously
        if not self.songs:
            self.label.config(text="Please select songs first.")
            return
        self.keep_playing = True
        self.playlist = self.songs[:]
        random.shuffle(self.playlist)
        self.current_index = 0
        threading.Thread(target=self._play_loop).start()

    def _play_loop(self):
        # Background loop to auto play shuffled songs
        while self.keep_playing:
            if self.current_index >= len(self.playlist):
                self.current_index = 0
                random.shuffle(self.playlist)
            self.play_song(self.playlist[self.current_index])
            threading.Thread(target=self.update_progress_loop, daemon=True).start()
            while pygame.mixer.music.get_busy() and self.keep_playing:
                time.sleep(0.5)
            if not self.is_paused:
                self.current_index += 1

    def update_progress_loop(self):
        # Continuously update progress bar
        while pygame.mixer.music.get_busy():
            self.update_progress()
            time.sleep(1)

    def update_selected_indices(self, event=None):
        # Store selected indices
        self.selected_indices = self.song_listbox.curselection()

    def play_selected_song(self):
        # Play first selected song
        if hasattr(self, 'selected_indices') and self.selected_indices:
            self.current_index = self.selected_indices[0]
            self.keep_playing = False
            self.playlist = self.songs[:]
            self.play_song(self.playlist[self.current_index])

    def play_song(self, song_path):
        # Load and play the selected song
        if os.path.exists(song_path):
            self.current_song = song_path
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            try:
                audio = MP3(song_path)
                self.total_duration = audio.info.length
            except:
                self.total_duration = 0
            name = os.path.basename(song_path)
            self.label.config(text=f"Now Playing:\n{name}")
            self.progress['value'] = 0
            self.time_label.config(text="00:00 / " + self.format_time(self.total_duration))

    def play_previous(self):
        # Play previous song
        if self.current_index > 0:
            self.current_index -= 1
            self.play_song(self.playlist[self.current_index])

    def play_next(self):
        # Play next song
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.play_song(self.playlist[self.current_index])

    def pause_resume(self):
        # Pause or resume the song
        if pygame.mixer.music.get_busy():
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.label.config(text=f"Resumed: {os.path.basename(self.current_song)}")
            else:
                pygame.mixer.music.pause()
                self.label.config(text="Paused")
            self.is_paused = not self.is_paused

    def stop(self):
        # Stop current playback
        self.keep_playing = False
        pygame.mixer.music.stop()
        self.label.config(text="Stopped")
        self.progress['value'] = 0
        self.time_label.config(text="00:00 / 00:00")

    def set_volume(self, val):
        # Set the playback volume
        volume = int(val) / 100
        pygame.mixer.music.set_volume(volume)

    def update_progress(self):
        # Update progress bar and time label
        try:
            pos = pygame.mixer.music.get_pos() / 1000
            percent = (pos / self.total_duration) * 100 if self.total_duration else 0
            self.progress['value'] = percent
            self.time_label.config(text=f"{self.format_time(pos)} / {self.format_time(self.total_duration)}")
        except:
            self.progress['value'] = 0

    def format_time(self, seconds):
        # Format seconds into MM:SS
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        return f"{minutes:02}:{sec:02}"

    def add_to_favorites(self):
        # Add selected songs to favorites
        selected_indices = self.song_listbox.curselection()
        if not selected_indices:
            self.label.config(text="No songs selected.")
            return

        for index in selected_indices:
            if index < len(self.songs):
                song_path = self.songs[index]
                self.favorites.add(song_path)

        self.update_song_list()
        self.label.config(text=f"{len(selected_indices)} songs added to favorites.")

    def save_favorites(self):
        # Save favorite songs to a file
        if not self.favorites:
            self.label.config(text="No favorites to save.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".fav", filetypes=[("Favorite List", "*.fav")])
        if filepath:
            with open(filepath, 'w') as file:
                for song in self.favorites:
                    file.write(song + '\n')
            self.label.config(text="Favorites saved.")

    def load_favorites(self):
        # Load favorite songs from a file
        filepath = filedialog.askopenfilename(filetypes=[("Favorite List", "*.fav")])
        if filepath:
            with open(filepath, 'r') as file:
                favs = set(line.strip() for line in file if os.path.exists(line.strip()))
            self.favorites.update(favs)
            self.update_song_list()

            if self.favorites:
                self.playlist = list(self.favorites)
                self.current_index = 0
                self.play_song(self.playlist[self.current_index])
                self.label.config(text=f"{len(favs)} favorites loaded and playing.")
            else:
                self.label.config(text="No valid favorites found.")


if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.mainloop()
