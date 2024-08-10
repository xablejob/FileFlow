import base64
import os
import uuid

from file_logic.models import File
from tests.conftest import UPLOAD_DIR_TEST


def create_test_file_by_api(client):
    # Создание тестового файла
    filename = "test_file.txt"
    file_content = b"Test content"
    file_base64 = base64.b64encode(file_content).decode()

    response = client.post(
        "/api/v1/files",
        json={"filename": filename, "file_base64": file_base64},
    )
    return response, filename, file_content


def test_upload_file(client):
    # Создание тестового файла
    response_create, filename, file_content = create_test_file_by_api(client)

    assert response_create.status_code == 202
    json_response = response_create.json()
    assert json_response["filename"] == filename
    assert json_response["size"] == len(file_content)
    assert os.path.exists(json_response["local_path"])


def test_get_file_metadata(client, db_session):
    # Создание тестового файла
    response_create, filename, _ = create_test_file_by_api(client)
    uid = response_create.json()["uid"]

    response_get = client.get(f"/api/v1/files/{uid}/metadata")
    assert response_get.status_code == 200
    json_response = response_get.json()
    assert json_response["filename"] == filename


def test_delete_file(client, db_session):
    # Создание тестового файла
    response_create, _, _ = create_test_file_by_api(client)
    uid = response_create.json()["uid"]

    response = client.delete(f"/api/v1/files/{uid}")
    assert response.status_code == 200
    assert response.json() == {"message": "File deleted successfully"}

    file_in_db = db_session.query(File).filter(File.uid == uid).first()
    assert file_in_db is None


def test_list_files(client, db_session):
    # Создание нескольких тестовых файлов
    file1 = File(
        uid=uuid.uuid4(),
        filename="file1.txt",
        size=100,
        format="text/plain",
        extension=".txt",
        local_path=os.path.join(UPLOAD_DIR_TEST, "file1.txt"),
    )
    file2 = File(
        uid=uuid.uuid4(),
        filename="file2.txt",
        size=200,
        format="text/plain",
        extension=".txt",
        local_path=os.path.join(UPLOAD_DIR_TEST, "file2.txt"),
    )
    db_session.add(file1)
    db_session.add(file2)
    db_session.commit()

    response = client.get("/api/v1/files")
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 2
