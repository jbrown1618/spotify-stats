from routes.utils import to_json
from data.provider import DataProvider

def producers_payload(track_uris=None):
    dp = DataProvider()
    producers = dp.producers(track_uris=track_uris)
    return to_json(producers, 'producer_mbid')