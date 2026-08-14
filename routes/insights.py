from data.repository import DataRepository
from routes.utils import to_json


repository = DataRepository()


def insights_payload(filters: dict):
    return {
        name: to_json(frame)
        for name, frame in repository.insight_frames(filters).items()
    }
