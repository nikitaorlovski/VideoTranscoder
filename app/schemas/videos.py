from typing import Literal

from pydantic import BaseModel, ConfigDict
import datetime

class VideoMeta(BaseModel):
    owner_id: int
    filename: str
    extension: str
    size: int


class VideoConvertResponse(BaseModel):
    video_id: str
    task_id: str
    status: str

class VideoResponse(BaseModel):
    uuid: str
    filename: str
    extension: str
    size: int
    path: str
    status: str
    owner_id: int
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class VideoFormatConvertRequest(BaseModel):
    target_format: Literal["mp4", "webm", "mov", "mkv", "avi"]