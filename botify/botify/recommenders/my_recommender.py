from .random import Random
from .recommender import Recommender
import random

border_of_good_track = 0.5


class MyRecommender(Recommender):
    """
    Works like Contextual recommender. The only difference is that this recommender replace a previous track
    by the last good one if the previous track isn't good enough. So it recommends something like the last good one,
    not a track that is near to the bad previous one.
    """

    def __init__(self, tracks_redis, catalog):
        self.tracks_redis = tracks_redis
        self.fallback = Random(tracks_redis)
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        if prev_track_time < border_of_good_track:
            previous_track = self.catalog.last_good_track_by_user.get(user)
        else:
            self.catalog.last_good_track_by_user[user] = previous_track

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations
        if not recommendations:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        shuffled = list(recommendations)
        random.shuffle(shuffled)
        return shuffled[0]
