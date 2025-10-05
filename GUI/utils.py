import tkinter as tk
from song_filter import match_nearest_neighbors_weighted
from tkinter import ttk
from sklearn.neighbors import NearestNeighbors
from Resources import config

matching_songs = []


# show adjectives on selection
def show_similar_songs_window(root, original_song, similar_songs):
    top = tk.Toplevel(root)
    top.title(f"Similar Songs to {original_song.clean_title}")
    top.geometry("400x300")

    ttk.Label(top, text=f"Songs similar to: {original_song.clean_title}", font=("Helvetica", 14)).pack(pady=10)

    listbox_similar = tk.Listbox(top, height=6, width=50)
    listbox_similar.pack(pady=10, padx=10, fill="both", expand=True)

    for song in similar_songs:
        listbox_similar.insert(tk.END, song.clean_title)

    ttk.Button(top, text="Close", command=top.destroy).pack(pady=10)


# Plot all songs
def update_plot(matching_indices, reduced_data, ax, canvas):
    ax.clear()

    ax.scatter(reduced_data[:, 0], reduced_data[:, 1], c="blue", label="All Songs", alpha=0.6)

    if matching_indices:
        ax.scatter(
            reduced_data[matching_indices, 0],
            reduced_data[matching_indices, 1],
            c="red",
            label="Matching Songs",
            alpha=0.8,
            edgecolor="black"
        )

    # Update labels and legend
    ax.set_title("Song Embeddings")
    ax.set_xlabel("Component 1")
    ax.set_ylabel("Component 2")

    # Redraw the plot
    canvas.draw()


def filter_songs(weights, result_listbox, indices, reduced_data, ax, canvas):
    # global selection_size
    # selected_indices = listbox_words.curselection()
    # selected_words = {all_words[i] for i in selected_indices}

    selected_words = {word: weights[word].get() for word in weights if weights[word].get() > 0}

    if not selected_words:
        result_listbox.delete(0, tk.END)
        result_listbox.insert(tk.END, "No words selected.")
        return

    # matching_songs, asw = match_nearest_neighbors(selected_words, selection_size=selection_size)
    matching_songs = match_nearest_neighbors_weighted(selected_words)
    # matching_songs = match_pairwise(selected_words)

    result_listbox.delete(0, tk.END)
    if matching_songs:
        for idx, song in enumerate(matching_songs):
            result_listbox.insert(tk.END, song.clean_title)
            if song.playlists:
                result_listbox.itemconfig(idx, {"bg": "blue"})
    else:
        result_listbox.insert(tk.END, "No matching songs found.")

    temp = [indices.index(song.id) for song in matching_songs]

    update_plot(temp, reduced_data, ax, canvas)
    # start here ------------
    return temp



def on_song_select(result_listbox, adj_songs, locations, weights):
    idx = result_listbox.curselection()[0]
    matching_songs = filter_songs(weights)
    selected_song = matching_songs[idx]
    nbrs = NearestNeighbors(n_neighbors=7, algorithm='auto').fit(locations)
    distances, indices = nbrs.kneighbors([selected_song.adjectives_.location[config.adj_type]])
    similair_songs = [adj_songs[idx] for idx in indices[0][1:]]
    show_similar_songs_window(selected_song, similair_songs)


