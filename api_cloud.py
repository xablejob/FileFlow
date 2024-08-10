import asyncio

from file_logic.models import File


async def request_upload_to_cloud(file: File):
    # Здесь должна быть реализация загрузки в облачное хранилище
    # Например, использование MinIO S3 или другого API
    cloud_path = f"https://example-cloud-storage.com/{file.uid}{file.extension}"
    await asyncio.sleep(2)  # Имитация задержки загрузки
    return cloud_path


async def request_delete_to_cloud(file: File):
    # Здесь должна быть реализация загрузки в облачное хранилище
    # Например, использование MinIO S3 или другого API
    cloud_path = f"https://example-cloud-storage.com/{file.uid}{file.extension}"
    await asyncio.sleep(2)  # Имитация задержки загрузки
    return cloud_path
