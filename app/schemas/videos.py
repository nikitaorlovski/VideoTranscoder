from pydantic import BaseModel

class VideoMeta(BaseModel):
    owner_id: int
    filename: str
    extension: str
    size: int


class VideoConvertResponse(BaseModel):
    video_id: str
    task_id: str
    status: str
