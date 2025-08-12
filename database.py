import sqlite3
import json
from pathlib import Path
import typing
import asyncio

# star_gifts_data.py faylidan faqat StarGiftData modelini import qilamiz
from star_gifts_data import StarGiftData
import constants
import utils

logger = utils.get_logger(__name__)

class Database:
    """
    Ma'lumotlar bazasi bilan ishlash uchun Singleton klassi.
    Bu butun dastur davomida faqat bitta ulanish (connection) bo'lishini ta'minlaydi.
    """
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: Path = constants.DB_FILEPATH):
        # Klass birinchi marta yaratilganda ulanishni o'rnatamiz
        if not hasattr(self, 'connection'):
            self.db_path = db_path
            # check_same_thread=False asinxron freymvorklarda ishlash uchun kerak
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.connection.cursor()
            logger.info(f"Database connection established to {db_path}")

    async def setup(self):
        """Ma'lumotlar bazasi jadvallarini yaratadi (agar mavjud bo'lmasa)."""
        async with self._lock:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS gifts (
                    id INTEGER PRIMARY KEY,
                    number INTEGER NOT NULL,
                    sticker_file_id TEXT NOT NULL,
                    sticker_file_name TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    convert_price INTEGER NOT NULL,
                    available_amount INTEGER NOT NULL,
                    total_amount INTEGER NOT NULL,
                    is_limited BOOLEAN NOT NULL,
                    first_appearance_timestamp INTEGER,
                    message_id INTEGER,
                    last_sale_timestamp INTEGER,
                    is_upgradable BOOLEAN DEFAULT FALSE,
                    last_checked_upgrade_id INTEGER,
                    live_topic_id INTEGER,
                    gift_slug TEXT
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            self.connection.commit()
            logger.info("Database tables ensured to exist.")

    async def save_gifts(self, gifts: list[StarGiftData]):
        """Bir nechta sovg'ani bir vaqtda bazaga yozadi (INSERT OR REPLACE)."""
        if not gifts:
            return
        async with self._lock:
            # Pydantic modelidan ustun nomlarini olamiz
            columns = StarGiftData.model_fields.keys()
            placeholders = ', '.join(['?'] * len(columns))
            sql = f"INSERT OR REPLACE INTO gifts ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Har bir sovg'a obyektini kortejga (tuple) o'tkazamiz
            gifts_data = [tuple(g.model_dump().values()) for g in gifts]
            
            self.cursor.executemany(sql, gifts_data)
            self.connection.commit()
            logger.debug(f"Saved/Updated {len(gifts)} gifts in the database.")

    async def load_all_gifts(self) -> list[StarGiftData]:
        """Barcha sovg'alarni bazadan o'qib, StarGiftData obyektlari ro'yxatini qaytaradi."""
        async with self._lock:
            self.cursor.execute("SELECT * FROM gifts ORDER BY id ASC")
            rows = self.cursor.fetchall()
            columns = [description[0] for description in self.cursor.description]
            gifts = [StarGiftData(**dict(zip(columns, row))) for row in rows]
            logger.info(f"Loaded {len(gifts)} gifts from database.")
            return gifts

    async def get_setting(self, key: str, default: typing.Any = None) -> typing.Any:
        """Sozlamalarni (masalan, chat_id) bazadan o'qiydi."""
        async with self._lock:
            self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = self.cursor.fetchone()
            if row:
                # Qiymatni to'g'ri turga (int) o'tkazib qaytaramiz
                try:
                    return int(row[0])
                except (ValueError, TypeError):
                    return default # Agar intga o'tmasa, standart qiymatni qaytaramiz
            return default

    async def set_setting(self, key: str, value: typing.Any):
        """Sozlamani bazaga yozadi."""
        async with self._lock:
            self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
            self.connection.commit()
            logger.info(f"Setting '{key}' updated to '{value}' in the database.")

# Butun dastur uchun yagona database obyektini yaratamiz
db = Database()
