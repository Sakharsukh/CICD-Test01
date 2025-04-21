import unittest
from tkinter import Tk
from spotify1 import MusicPlayer
import os
from tkinter import filedialog
def select_song_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        return [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".mp3")]
    return []
class TestMusicPlayer(unittest.TestCase):
    def setUp(self):
        # Set up the Tkinter root and MusicPlayer instance
        self.root = Tk()
        self.player = MusicPlayer(self.root)

    def tearDown(self):
        # Destroy the Tkinter root after each test
        self.root.destroy()

    def test_select_songs(self):
        # Test that songs can be selected and added to the list
        self.player.songs = ["song1.mp3", "song2.mp3"]
        self.player.update_song_listbox()
        self.assertEqual(self.player.song_listbox.size(), 2)
        self.assertEqual(self.player.songs, ["song1.mp3", "song2.mp3"])

    def test_set_volume(self):
        # Test that volume can be set correctly
        self.player.set_volume(50)
        self.assertAlmostEqual(self.player.volume_slider.get(), 50)

    def test_add_to_favorites(self):
        # Test adding a song to favorites
        self.player.songs = ["song1.mp3"]
        self.player.current_song = "song1.mp3"
        self.player.add_to_favorites()
        self.assertIn("song1.mp3", self.player.favorites)

    def test_save_and_load_favorites(self):
        # Test saving and loading favorites
        self.player.favorites = {"song1.mp3", "song2.mp3"}
        self.player.save_favorites()
        self.player.favorites.clear()
        self.player.load_favorites()
        self.assertIn("song1.mp3", self.player.favorites)
        self.assertIn("song2.mp3", self.player.favorites)

    def test_play_previous(self):
        # Test playing the previous song
        self.player.songs = ["song1.mp3", "song2.mp3"]
        self.player.current_index = 1
        self.player.play_previous()
        self.assertEqual(self.player.current_index, 0)

    def test_play_selected_song(self):
        # Test playing a selected song
        self.player.songs = ["song1.mp3", "song2.mp3"]
        self.player.song_listbox.insert(0, "song1.mp3")
        self.player.song_listbox.selection_set(0)
        self.player.play_selected_song()
        self.assertEqual(self.player.current_song, "song1.mp3")

    def test_pause_resume(self):
        # Test pausing and resuming a song
        self.player.is_paused = False
        self.player.pause_resume()
        self.assertTrue(self.player.is_paused)
        self.player.pause_resume()
        self.assertFalse(self.player.is_paused)

    def test_stop(self):
        # Test stopping the song
        self.player.current_song = "song1.mp3"
        self.player.stop()
        self.assertEqual(self.player.current_song, "")

    def test_play_random(self):
        # Test playing a random song
        self.player.songs = ["song1.mp3", "song2.mp3", "song3.mp3"]
        self.player.play_random()
        self.assertIn(self.player.current_song, self.player.songs)

    def test_update_song_listbox(self):
        # Test updating the song listbox
        self.player.songs = ["song1.mp3", "song2.mp3"]
        self.player.update_song_listbox()
        self.assertEqual(self.player.song_listbox.size(), 2)

if __name__ == "__main__":
    unittest.main()