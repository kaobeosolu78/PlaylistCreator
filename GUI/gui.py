import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import on_song_select, filter_songs, update_plot
from settings import selection_size_menu, group_selection_menu
from spotify_handler import create_playlist
from Resources import config


def init_vars():
    import random
    from Songs import Songs
    from sklearn.manifold import TSNE
    import numpy as np

    def init_wordlist(adj_songs):
        hist = {}
        for song in adj_songs:
            for adj, emb in song.adjectives_.by_type(config.adj_type):
                hist[adj] = hist.get(adj, 0) + 1
        hist = dict(sorted(hist.items(), key=lambda x: x[1], reverse=True))
        listed_words = list(hist.keys())[:100]
        random.shuffle(listed_words)
        return listed_words

    def init_group_wordlist():
        from song_filter import prep_group
        from AdjCluster import AdjRoot


        adjs = AdjRoot()
        adjs.load('knn_sim_words')

        group_embeddings, all_adjs = prep_group(adjs)

        listed_words = ['\n, '.join(tuple(sorted([str(i) for i in items[1][1]]))) for items in list(all_adjs)[:200]]
        random.shuffle(listed_words)
        return listed_words

    songs = Songs()
    songs.load(config.song_set)
    # songs.load('vibe_playlist_songs')
    # songs.load('vibe_album_songs')

    adj_songs = songs.contains_adjs()


    listed_words = init_wordlist(adj_songs)
    if config.group_selection:
        listed_words = init_group_wordlist()


    indices = [song.id for song in adj_songs]



    locations = [song.adjectives_.location[config.adj_type] for song in adj_songs]
    dr = TSNE(n_components=2)
    # dr = PCA(n_components=2)
    reduced_data = dr.fit_transform(np.array(locations))
    return adj_songs, listed_words, reduced_data, indices


def setup_gui(root):
    """Sets up the main GUI layout."""
    adj_song, listed_words, reduced_data, indices = init_vars()
    weights = {}

    # Headings
    tk.Label(root, text="Select Descriptive Words", font=("Helvetica", 18)).pack(pady=10)

    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 12))
    style.configure("TButton", font=("Helvetica", 12), padding=5)
    style.configure("TFrame", padding=10)

    main_frame = ttk.Frame(root)
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side="right", padx=10, fill="both", expand=True)

    results_frame = ttk.Frame(right_frame)
    results_frame.pack(side="left", fill="both", expand=True, padx=5)


    # Graph
    plot_frame = ttk.Frame(right_frame)
    plot_frame.pack(side="left", fill="both", expand=True, padx=5)

    fig, ax = plt.subplots(figsize=(5, 4))
    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)


    # Matching Songs Listbox
    ttk.Label(right_frame, text="Matching Songs").pack(pady=5)
    result_listbox = tk.Listbox(right_frame, selectmode='multiple', height=15, width=50)
    result_listbox.bind("<<ListboxSelect>>", on_song_select)

    scrollbar_results = ttk.Scrollbar(right_frame, orient="vertical", command=result_listbox.yview)
    result_listbox.config(yscrollcommand=scrollbar_results.set)
    scrollbar_results.pack(side="right", fill="y")
    result_listbox.pack(side="left", fill="both", expand=True)


    # Weight Sliders
    on_slider_change = lambda event: update_plot(*(filter_songs(weights, result_listbox, indices, reduced_data, ax, canvas), reduced_data, ax, canvas))


    slider_frame_container = ttk.Frame(main_frame)
    slider_frame_container.pack(side="left", padx=10, fill="both", expand=True)

    slider_canvas = tk.Canvas(slider_frame_container)
    scrollable_slider_frame = ttk.Frame(slider_canvas)
    scrollbar_sliders = ttk.Scrollbar(slider_frame_container, orient="vertical", command=slider_canvas.yview)

    slider_canvas.configure(yscrollcommand=scrollbar_sliders.set)
    scrollbar_sliders.pack(side="right", fill="y")
    slider_canvas.pack(side="left", fill="both", expand=True)
    slider_canvas.create_window((0, 0), window=scrollable_slider_frame, anchor="nw")

    ttk.Label(scrollable_slider_frame, text="Adjust Weights for Words").pack(pady=5)

    for word in listed_words:
        frame = ttk.Frame(scrollable_slider_frame)
        frame.pack(fill="x", padx=5, pady=2)

        label = ttk.Label(frame, text=word, width=15)
        label.pack(side="left")

        weights[word] = tk.DoubleVar(value=0)  # Default weight is 1.0
        slider = ttk.Scale(frame, from_=0, to=10, orient="horizontal", variable=weights[word])
        slider.pack(side="right", fill="x", expand=True)

        slider.bind("<Motion>", on_slider_change)  # Updates on motion
        slider.bind("<ButtonRelease-1>", on_slider_change)  # Updates when released


    update_scroll_region = lambda event: slider_canvas.configure(scrollregion=slider_canvas.bbox("all"))
    scrollable_slider_frame.bind("<Configure>", update_scroll_region)

    # Menu Setup
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    settings_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="Set Selection Size", command=lambda: selection_size_menu())
    settings_menu.add_command(label="Toggle Group Adj Search", command=lambda: group_selection_menu())

    # Button for Playlist Creation
    button_frame = ttk.Frame(root)
    button_frame.pack(side="bottom", pady=20)
    ttk.Button(button_frame, text="Create Spotify Playlist", command=create_playlist).pack(side="left", padx=10)

    return result_listbox