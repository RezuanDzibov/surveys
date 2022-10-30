import json
from uuid import UUID


def uuid_to_str(object_) -> str:
    if isinstance(object_, UUID):
        return str(object_)


async def serialize_uuid_to_str(to_serialize: dict) -> dict:
    return json.loads(json.dumps(to_serialize, default=uuid_to_str))
