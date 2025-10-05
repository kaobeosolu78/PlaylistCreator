import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tkinter import messagebox

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="http://localhost:8888/callback",
    scope="playlist-modify-public"
))


def create_playlist(matching_songs):
    if not matching_songs:
        messagebox.showerror("Error", "No songs to add to the playlist.")
        return

    user_id = sp.me()["id"]
    playlist_name = 'Traits-Based Playlist'
    playlist_description = "Generated based on selected adjectives."
    playlist = sp.user_playlist_create(user_id, name=playlist_name, public=True, description=playlist_description)

    playlist_id = playlist["id"]
    track_uris = [song.data['uri'] for song in matching_songs]
    if track_uris:
        sp.playlist_add_items(playlist_id, track_uris)

    messagebox.showinfo("Success", f"Playlist '{playlist_name}' created with {len(track_uris)} tracks!")