import base64
import io
import uuid
from typing import List

import uvicorn
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

import schemas
from db_utils.database import get_db
from file_logic import crud
from utils import get_upload_dir, lifespan

app = FastAPI(
    title="File Storage API",
    description="API для хранения файлов",
    version="0.0.1",
    lifespan=lifespan,
)


@app.post(
    "/api/v1/files",
    tags=["api"],
    response_model=schemas.File,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: schemas.FileBase64,
    db: Session = Depends(get_db),
    upload_dir: str = Depends(get_upload_dir),
):
    """
    Функция для создания файла из строки base64.
    Возвращает информацию о загруженном файле.
    """
    # Декодируем строку base64
    file_data = base64.b64decode(file.file_base64)
    # Создаем объект BytesIO из декодированных данных
    file_like = io.BytesIO(file_data)
    # Создаем объект UploadFile
    upload_file = UploadFile(file=file_like, filename=file.filename)
    return await crud.create_file(db, upload_file, background_tasks, upload_dir)


@app.post(
    "/api/v1/files/stream",
    tags=["api"],
    response_model=schemas.File,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_file_stream(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    upload_dir: str = Depends(get_upload_dir),
):
    """
    Функция для создания файла с потоковой загрузкой.
    Возвращает информацию о загруженном файле.
    """
    return await crud.create_file(db, file, background_tasks, upload_dir)


@app.get(
    "/api/v1/files/{uid}",
    tags=["api"],
    response_class=FileResponse,
)
async def get_file(uid: uuid.UUID, db: Session = Depends(get_db)):
    """
    Функция для получения файла по его UID.
    Возвращает файл в виде ответа с заголовком Content-Disposition.
    """
    file_data = crud.get_file(db, uid)
    if file_data is None:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_data.local_path, filename=file_data.filename)


@app.get(
    "/api/v1/files/{uid}/metadata",
    tags=["api"],
    response_model=schemas.File,
)
async def get_file_metadata(uid: uuid.UUID, db: Session = Depends(get_db)):
    """
    Функция для получения метаданных файла по его UID.
    Возвращает информацию о файле.
    """
    file_data = crud.get_file(db, uid)
    if file_data is None:
        raise HTTPException(status_code=404, detail="File not found")
    return file_data


@app.get("/api/v1/files", tags=["api"], response_model=List[schemas.File])
async def list_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Функция для получения списка файлов.
    Возвращает список файлов.
    """
    return crud.get_files(db, skip=skip, limit=limit)


@app.delete("/api/v1/files/{uid}", tags=["api"])
async def delete_file(uid: uuid.UUID, db: Session = Depends(get_db)):
    """
    Функция для удаления файла по его UID.
    Возвращает сообщение об успешном удалении.
    """
    if await crud.delete_file(db, uid):
        return {"message": "File deleted successfully"}
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/static/index.html", tags=["frontend"])
async def main1():
    """Пример frontend для загрузки файлов"""
    content = """
    <body>
        <form action="/api/v1/files/stream" enctype="multipart/form-data" method="post">
            <input name="file" type="file" multiple>
            <input type="submit">
        </form>
    </body>
    """
    return HTMLResponse(content=content)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8123, reload=True)
