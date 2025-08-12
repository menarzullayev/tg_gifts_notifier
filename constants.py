from pathlib import Path


ENCODING = "utf-8"

WORK_DIRPATH = Path(__file__).parent
LOGS_DIRPATH = WORK_DIRPATH / "logs"

# JSON fayl yo'li o'rniga SQLite ma'lumotlar bazasi fayli yo'lini ko'rsatamiz
DB_FILEPATH = WORK_DIRPATH / "gifts_data.sqlite"

LOG_FILEPATH = LOGS_DIRPATH / "main.log"


if not LOGS_DIRPATH.exists():
    LOGS_DIRPATH.mkdir()
