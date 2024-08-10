import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FileBase(BaseModel):
    filename: str
    size: int
    format: Optional[str]
    extension: str


class File(FileBase):
    uid: uuid.UUID
    local_path: str
    cloud_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FileBase64(BaseModel):
    filename: str
    file_base64: str
