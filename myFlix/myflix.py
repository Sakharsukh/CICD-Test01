import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import json

class MyFlixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MyFlix")
        self.root.geometry("800x600")
        self.root.configure(bg="black")

        # Movie data with poster paths
        self.movies = {
            "Movie 1": "posters/movie1.jpg",
            "Movie 2": "posters/movie2.jpg",
            "Movie 3": "posters/movie3.jpg"
        }

        # Path for favorites storage
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        # Set up UI
        self.setup_ui()

    def setup_ui(self):
        # Title label
        tk.Label(self.root, text="🎬 MyFlix", font=("Helvetica", 24, "bold"), fg="white", bg="black").pack(pady=10)

        # Frame to hold movie posters and favorite buttons
        movie_frame = tk.Frame(self.root, bg="black")
        movie_frame.pack(pady=20)

        # Loop through each movie to display the poster and favorite button
        for idx, (movie, poster) in enumerate(self.movies.items()):
            try:
                # Debugging: Check if the image file exists
                print(f"Loading poster for: {movie}, {poster}")
                
                # Load image and resize
                img = Image.open(poster).resize((150, 220))
                photo = ImageTk.PhotoImage(img)
                
                # Create button for movie poster
                btn = tk.Button(movie_frame, image=photo, command=lambda m=movie: self.play_movie(m), bd=0)
                btn.image = photo
                btn.grid(row=0, column=idx, padx=15)

                # Favorite button (empty or filled star)
                fav_btn = tk.Button(movie_frame, text="★" if movie in self.favorites else "☆",
                                    command=lambda m=movie: self.toggle_favorite(m), fg="yellow", bg="black", bd=0,
                                    font=("Helvetica", 14))
                fav_btn.grid(row=1, column=idx)

            except Exception as e:
                print(f"Error loading {poster}: {e}")
                messagebox.showerror("Error", f"Error loading image for {movie}. Please check the file path.")

        # Button to show favorite movies
        fav_button = tk.Button(self.root, text="❤️ Show Favorites", command=self.show_favorites, font=("Helvetica", 14),
                               bg="red", fg="white")
        fav_button.pack(pady=10)

    def play_movie(self, movie_name):
        # Placeholder for movie playback (currently just a message)
        top = tk.Toplevel(self.root)
        top.title("Now Playing")
        top.geometry("400x200")
        label = tk.Label(top, text=f"Now Playing: {movie_name}", font=("Helvetica", 14), fg="red")
        label.pack(pady=30)

        msg = tk.Label(top, text="(Video playback not supported in Python 3.13)", fg="white", bg="black")
        msg.pack(pady=10)

    def toggle_favorite(self, movie_name):
        # Toggle the movie between favorite and non-favorite
        if movie_name in self.favorites:
            self.favorites.remove(movie_name)
        else:
            self.favorites.append(movie_name)
        self.save_favorites()
        self.refresh_ui()

    def show_favorites(self):
        # Show a list of favorite movies in a message box
        fav_list = "\n".join(self.favorites) if self.favorites else "No favorites yet!"
        messagebox.showinfo("Your Favorites", fav_list)

    def load_favorites(self):
        # Load the favorites from the favorites.json file
        if os.path.exists(self.favorites_file):
            with open(self.favorites_file, "r") as f:
                return json.load(f)
        return []

    def save_favorites(self):
        # Save the favorites list to a JSON file
        with open(self.favorites_file, "w") as f:
            json.dump(self.favorites, f)

    def refresh_ui(self):
        # Refresh the UI (reload the entire interface)
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()


if __name__ == "__main__":
    # Check if 'posters' folder exists, if not create it
    if not os.path.exists("posters"):
        os.makedirs("posters")
        print("Please add movie poster images in the 'posters' folder and restart the app.")
    else:
        # Check if poster images exist, else notify the user
        if not all(os.path.exists(f"posters/{poster}") for poster in ["movie1.jpg", "movie2.jpg", "movie3.jpg"]):
            print("Some poster images are missing in the 'posters' folder. Please add them and restart the app.")
        else:
            root = tk.Tk()
            app = MyFlixApp(root)
            root.mainloop()
