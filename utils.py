import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from db_utils.database import Base, SessionLocal, engine
from file_logic import crud
from settings_app import CLEAN_OLD_FILES_DAYS, UPLOAD_DIR


async def clean_old_files_job():
    """
    Функция для очистки старых файлов.
    Ежедневно удаляет файлы старше CLEAN_OLD_FILES_DAYS дней.
    """
    db = SessionLocal()
    try:
        await crud.clean_old_files(db, CLEAN_OLD_FILES_DAYS)
    finally:
        db.close()


def create_uploads_directory():
    """
    Функция для создания папки, если она не существует
    """
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)


@asynccontextmanager
async def lifespan(app):
    # Создаем таблицы в базе данных
    Base.metadata.create_all(bind=engine)
    create_uploads_directory()

    # Настройка планировщика для очистки старых файлов
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(hour=20, minute=0)  # Запускаем каждые день в 20:00
    scheduler.add_job(clean_old_files_job, trigger)
    scheduler.start()

    yield

    scheduler.shutdown()


def get_upload_dir():
    yield UPLOAD_DIR
