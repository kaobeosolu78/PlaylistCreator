import numpy as np
from sklearn.metrics import pairwise_distances



class Adjectives:
    def __init__(self, typing=('all',), adjectives=[], embeddings=[], types_=[]):
        self.adjectives_, self.embeddings_, self.types = adjectives, embeddings, types_
        self.typing = typing

    def __len__(self):
        return len(self.adjectives_)

    def __iter__(self):
        for k in range(len(self)):
            yield (self.adjectives_[k], self.embeddings_[k])

    def __bool__(self):
        if self.adjectives_:# and sorted(self.typing) == sorted(set(['all', *set(self.types)])):
            return True
        return False

    def __getitem__(self, item):
        if item in self.types:
            yield from self.by_type(item)

        if type(item) == int:
            yield (self.adjectives_[item], self.embeddings_[item])


    def add(self, adjective, embedding, type_=None):
        self.types.append(type_)
        self.embeddings_.append(embedding)
        self.adjectives_.append(adjective)

    def by_type(self, type_):
        if type_ == 'all':
            yield from self
        else:
            for idx in range(len(self.types)):
                if self.types[idx] == type_:
                    yield from self[idx]

    @property
    def location(self):
        embeddings = {type_: np.mean(np.array([emb for adj, emb in self.by_type(type_) if emb is not None]), axis=0) for type_ in self.typing}
        embeddings.update({'all': np.mean(np.array([emb for adj, emb in self if emb is not None]), axis=0)})
        return embeddings

    @property
    def pairwise(self):
        product = {}
        for typ in self.typing:
            pd = pairwise_distances([emb for adj, emb in self.by_type(typ)])
            product[typ] = np.mean(pd[np.triu_indices_from(pd, k=1)])
        return product

    @property
    def rep(self):
        for k in range(len(self)):
            yield (self.types[k], self.adjectives_[k])



