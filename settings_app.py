DATABASE_URL = "postgresql://user_app:db@localhost:8124"
APP_DATABASE_URL = f"{DATABASE_URL}/db"
TEST_DATABASE_URL = f"{DATABASE_URL}/testdb"

UPLOAD_DIR = "uploads"
CHUNK_SIZE = 1024 * 1024  # 1 MB

# Настройки очистки локального диска
# Количество дней для удаления файлов старше этого количества
CLEAN_OLD_FILES_DAYS = 30
# Количество дней для удаления файлов без использования
CLEAN_FILES_NO_USE_DAYS = 1
