import numpy as np
import pickle
from sklearn.metrics import pairwise_distances
from sklearn.manifold import TSNE
from Adjectives import Adjectives

clean = lambda item: ''.join(char for char in item if char.isalnum() or char == ' ')



class Songs(list):
    def __init__(self, songs=[], *args, **kwargs):
        super().__init__(songs)
        # ItemBase.__init__(self, *args, **kwargs)

        self.index = {'songs': {}, 'artists': {}}
        for idx, song in enumerate(self):
            song_ = song.title
            self.index['songs'][song_] = self.index['songs'].get(song_, []) + [idx]
            for artist in song.artists:
                self.index['artists'][artist] = self.index['artists'].get(artist, []) + [idx]


    def search(self, song_name='', artist_name='', queries=[], clean_=True, lower=True):
        s, a = self.index['songs'], self.index['artists']
        if lower:
            song_name, artist_name = song_name.lower(), artist_name.lower()
            temp_s, temp_a = {}, {}
            for k, v in s.items():
                word = k.lower()
                temp_s[word] = set(temp_s.get(word, {})) | set(v)
            s = temp_s

            for k, v in a.items():
                word = k.lower()
                temp_a[word] = set(temp_a.get(word, {})) | set(v)
            a = temp_a

        if clean_:
            song_name, artist_name = clean(song_name), clean(artist_name)
            temp_s, temp_a = {}, {}
            for k, v in s.items():
                word = clean(k)
                temp_s[word] = set(temp_s.get(word, {})) | set(v)
            s = temp_s

            for k, v in a.items():
                word = clean(k)
                temp_a[word] = set(temp_a.get(word, {})) | set(v)
            a = temp_a


        if not queries:
            queries = [(song_name, artist_name)]

        for sn, an in queries:
            if sn and an:
                yield set(s.get(sn, [])).intersection(set(a.get(an, [])))

            elif sn:
                yield s.get(sn, [])

            elif an:
                yield a.get(an, [])



    def save(self, key=''):
        if not key:
            key = self.key
            if not key:
                print('enter a save key')

        with open(f'SourceData/{key}.pkl', 'wb') as f:
            pickle.dump((self[:], self.__dict__), f, pickle.HIGHEST_PROTOCOL)
        print()

    def load(self, key=''):
        if not key:
            key = self.key
            if not self.key:
                print('enter a load key')

        with open(f'/Users/kaobeosolu/PycharmProjects/PlaylistCreator/Source/Resources/{key}.pkl', 'rb') as f:
            items, dic = pickle.load(f)
        super().__init__(items)
        self.__dict__ = dic

    def contains_adjs(self):
        return Songs([item for item in self if item.adjectives_], key='contains_adjs', description='all songs from playlist_songs that have an entry in adjective dict.')

    def dict_adjs(self):
        product = {}
        for song in self:
            for key, value in song.adjectives_.items():
                product[key] = value
        return product

    def histogram(self, adj_type):
        product = {}
        for song in self:
            for key, val in song.adjectives_[adj_type]:
                product[key] = product.get(key, 0) + 1
        product = dict(sorted(product.items(), key=lambda item: item[1], reverse=True))
        return product

    # def pairwise(self, adj_type='melody'):
    #     adjs = self.contains_adjs()
    #     locations = [item.location[adj_type] for item in adjs]
    #     pd = pairwise_distances(np.array(locations))
    #     return np.mean(pd[np.triu_indices_from(pd, k=1)])


    def by_artist(self):
        product = {}
        for song in self:
            artist = song.artists[0]
            product[artist] = product.get(artist, []) + [song]
        return {key: Songs(val, key=key, description=f'Songs made by the artist {key}') for key, val in product.items()}

    def by_album(self):
        product = {}
        albums = []
        for song in self:
            album = song.data['album']['name']
            albums.append(song.data['album'])
            product[album] = product.get(album, []) + [song]
        return {key: Songs(val, key=key, description=f'Songs that are from the album {key}') for key, val in product.items()}, albums

    def by_playlist(self):
        product = {pl: [] for s in self for pl in s.playlists}
        for pl in product:
            for song in self:
                if pl in song.playlists:
                    product[pl].append(song)
        return product

    def by_id(self, id_):
        for item in self:
            if item.id == id_:
                return item
        return None





class Song:
    def __init__(self, data, typing=(), adjectives=[], embeddings=[], types_=[], playlists=[]):
        self.data = data
        self.adjectives_ = Adjectives(typing if typing else ('all',), adjectives=adjectives, embeddings=embeddings, types_=types_)
        self.playlists = playlists

    @property
    def title(self):
        return self.data['name']

    @property
    def artists(self):
        return tuple(sorted([item['name'] for item in self.data['artists']]))

    @property
    def id(self):
        return self.data['id']

    @property
    def clean_title(self):
        if not self.__dict__.get('clean_title_'):
            self.clean_title_ = clean(self.title)
        return self.clean_title_

    @property
    def clean_artists(self):
        if not self.__dict__.get('clean_artists_'):
            self.clean_artists_ = tuple([clean(artist) for artist in self.artists])
        return self.clean_artists_

    @property
    def adjectives(self):
        return [(adj, emb) for adj, emb in self.adjectives_]

    @property
    def location(self):
        return self.adjectives_.location



