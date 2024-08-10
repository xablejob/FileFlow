import uuid

from sqlalchemy import BigInteger, Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID

from db_utils.database import Base


class File(Base):
    __tablename__ = "files"

    uid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        index=True,
        default=uuid.uuid4,
    )
    filename = Column(String, index=True, comment="Оригинальное имя файла")
    size = Column(BigInteger, comment="Рамер файла в байтах")
    format = Column(
        String,
        nullable=True,
        comment='Формат файла (например, "image", "video", "audio")',
    )
    extension = Column(String, comment="Расширение файла")
    local_path = Column(String, comment="Путь к файлу на локальном диске")
    cloud_path = Column(
        String, nullable=True, comment="Путь к файлу в облачном хранилище"
    )
    created_at = Column(
        DateTime, server_default=func.now(), comment="Дата и время создания записи"
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата и время последнего обновления записи",
    )
    last_download = Column(
        DateTime, nullable=True, comment="Дата и время последней загрузки"
    )
