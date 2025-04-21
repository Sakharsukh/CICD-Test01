import unittest
from unittest.mock import patch, MagicMock
from spotify import MusicPlayer
import tkinter as tk
import pygame

class TestMusicPlayer(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        self.root = tk.Tk()
        self.player = MusicPlayer(self.root)

    def tearDown(self):
        """Destroy the Tkinter root window after each test."""
        self.root.destroy()

    @patch('spotify.spotify.filedialog.askopenfilenames')
    def test_select_songs(self, mock_askopenfilenames):
        """Test selecting songs."""
        mock_askopenfilenames.return_value = ["song1.mp3", "song2.mp3"]
        self.player.select_songs()
        self.assertEqual(self.player.songs, ["song1.mp3", "song2.mp3"])
        self.assertEqual(self.player.song_listbox.size(), 2)

    @patch('spotify.spotify.filedialog.asksaveasfilename')
    @patch('builtins.open', new_callable=MagicMock)
    def test_save_favorites(self, mock_open, mock_asksaveasfilename):
        """Test saving favorite songs."""
        self.player.favorites = {"song1.mp3", "song2.mp3"}
        mock_asksaveasfilename.return_value = "favorites.fav"
        self.player.save_favorites()
        mock_open.assert_called_once_with("favorites.fav", 'w')
        mock_open().write.assert_any_call("song1.mp3\n")
        mock_open().write.assert_any_call("song2.mp3\n")

    @patch('spotify.spotify.filedialog.askopenfilename')
    @patch('builtins.open', new_callable=MagicMock)
    def test_load_favorites(self, mock_open, mock_askopenfilename):
        """Test loading favorite songs."""
        mock_askopenfilename.return_value = "favorites.fav"
        mock_open.return_value.__enter__.return_value = ["song1.mp3\n", "song2.mp3\n"]
        with patch('os.path.exists', return_value=True):
            self.player.load_favorites()
        self.assertEqual(self.player.favorites, {"song1.mp3", "song2.mp3"})

    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    def test_play_song(self, mock_play, mock_load):
        """Test playing a song."""
        with patch('os.path.exists', return_value=True):
            with patch('pygame.mixer.Sound') as mock_sound:
                mock_sound.return_value.get_length.return_value = 120
                self.player.play_song("song1.mp3")
                mock_load.assert_called_once_with("song1.mp3")
                mock_play.assert_called_once()
                self.assertEqual(self.player.current_song, "song1.mp3")
                self.assertEqual(self.player.total_duration, 120)

    @patch('pygame.mixer.music.pause')
    @patch('pygame.mixer.music.unpause')
    def test_pause_resume(self, mock_unpause, mock_pause):
        """Test pausing and resuming a song."""
        self.player.is_paused = False
        with patch('pygame.mixer.music.get_busy', return_value=True):
            self.player.pause_resume()
            mock_pause.assert_called_once()
            self.assertTrue(self.player.is_paused)
            self.player.pause_resume()
            mock_unpause.assert_called_once()
            self.assertFalse(self.player.is_paused)

    @patch('pygame.mixer.music.stop')
    def test_stop(self, mock_stop):
        """Test stopping the music."""
        self.player.stop()
        mock_stop.assert_called_once()
        self.assertFalse(self.player.keep_playing)
        self.assertEqual(self.player.progress['value'], 0)

    @patch('pygame.mixer.music.set_volume')
    def test_set_volume(self, mock_set_volume):
        """Test setting the volume."""
        self.player.set_volume(50)
        mock_set_volume.assert_called_once_with(0.5)

if __name__ == '__main__':
    unittest.main()