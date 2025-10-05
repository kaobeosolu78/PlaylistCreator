import numpy as np
from sklearn.neighbors import NearestNeighbors
import pickle
from Songs import Songs
from Resources import config

songs = Songs()
songs.load(config.song_set)#'playlist_songs')

adj_songs = songs.contains_adjs()

with open('/Users/kaobeosolu/PycharmProjects/Test1/GUI/sourcedata/embeddings.pkl', 'rb') as f:
    embeddings = pickle.load(f)



def prep_group(adjs):
    temp = adjs.get_match_ratios()
    temp = temp[:200]
    temp = adjs.process_match_ratios()

    temp = adjs

    # all_adjs = {item[1][0]: [str(i) for i in item[1][1]] for item in Objects}
    # for adj in embeddings:
    #     if not all_adjs.get(adj):
    #         all_adjs[adj] = [adj]

    group_embeddings = embeddings.copy()
    # for adj in all_adjs:
    #     group_embeddings[adj] = np.mean([embeddings[a] for a in all_adjs[adj]])

    for item in temp:
        group_embeddings['\n, '.join(tuple(sorted([i.key for i in item[1][1]])))] = np.mean([embeddings[a.key] for a in item[1][1]], axis=0)

    return group_embeddings, temp


locations = [song.adjectives_.location[config.adj_type] for song in adj_songs]


def match_nearest_neighbors_weighted(selected_weights):
    embeddings_ = embeddings

    all_weights = np.zeros_like(next(iter(embeddings_.values())))
    total_weight = sum(selected_weights.values())

    for word, weight in selected_weights.items():
        if word in embeddings_:
            all_weights += embeddings_[word] * (weight / total_weight)

    nbrs = NearestNeighbors(n_neighbors=len(locations) if len(locations) < config.selection_size else config.selection_size, algorithm='auto').fit(locations)
    distances, indices = nbrs.kneighbors([all_weights])

    return [adj_songs[idx] for idx in indices[0]]