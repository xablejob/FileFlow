import os
import uuid
from datetime import datetime, timedelta
from itertools import chain

import aiofiles
from fastapi import BackgroundTasks, UploadFile
from sqlalchemy.orm import Session

from api_cloud import request_delete_to_cloud, request_upload_to_cloud
from file_logic.models import File
from settings_app import CHUNK_SIZE, CLEAN_FILES_NO_USE_DAYS


async def create_file(
    db: Session, file: UploadFile, background_tasks: BackgroundTasks, upload_dir: str
):
    """Функция для создания файла с асинхронной загрузкой"""
    file_uid = uuid.uuid4()
    filename = file.filename
    size = 0
    format = file.content_type
    extension = os.path.splitext(filename)[1]

    local_path = os.path.join(upload_dir, f"{file_uid}{extension}")

    async with aiofiles.open(local_path, "wb") as buffer:
        while content := await file.read(CHUNK_SIZE):
            await buffer.write(content)
            size += len(content)

    db_file = File(
        uid=file_uid,
        filename=filename,
        size=size,
        format=format,
        extension=extension,
        local_path=local_path,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    # Асинхронная отправка в облачное хранилище
    background_tasks.add_task(upload_to_cloud, db, db_file)

    return db_file


def get_file(db: Session, uid: uuid.UUID):
    """Функция для получения файла по его UID"""
    file = db.query(File).filter(File.uid == uid).first()
    if file:
        # Обновить дату последнего скачивания для данного файла
        file.last_download = datetime.utcnow()
        db.add(file)
        db.commit()
    return file


def get_files(db: Session, skip: int = 0, limit: int = 100):
    """Функция для получения списка файлов"""
    return db.query(File).offset(skip).limit(limit).all()


async def upload_to_cloud(db: Session, file: File):
    """Загрузка файла в облако"""
    try:
        cloud_path = await request_upload_to_cloud(file)
        file.cloud_path = cloud_path

        db.add(file)
        db.commit()
    except Exception as e:
        db.rollback()  # Откат транзакции в случае ошибки
        print(f"Ошибка при загрузке в облако: {e}")


async def clean_old_files(db: Session, days: int):
    """Функция для удаления старых файлов"""
    # Удаление файлов старше определенного количества дней
    cutoff_date_old = datetime.utcnow() - timedelta(days=days)
    old_files = db.query(File).filter(File.updated_at < cutoff_date_old).all()
    # Удаляем файлы без даты последнего скачивания, которые старше 1 дня
    cutoff_day_no_use = datetime.utcnow() - timedelta(days=CLEAN_FILES_NO_USE_DAYS)
    no_use_file = (
        db.query(File)
        .filter(File.updated_at < cutoff_day_no_use, File.last_download == None)  # noqa
        .all()
    )
    for file in chain(old_files, no_use_file):
        await delete_file(db, file.uid)


async def delete_file(db: Session, uid: uuid.UUID):
    """Функция для удаления файла по его UID"""
    file = db.query(File).filter(File.uid == uid).first()
    if file:
        if os.path.exists(file.local_path):
            os.remove(file.local_path)
        db.delete(file)
        db.commit()

        await request_delete_to_cloud(file)

        return True
    return False
