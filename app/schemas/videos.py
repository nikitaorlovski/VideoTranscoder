from pydantic import BaseModel


class VideoMeta(BaseModel):
    owner_id: int
    filename: str
    extension: str
    size: int
