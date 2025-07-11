# config.py
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

import constants

# .env faylidan o'zgaruvchilarni yuklash (mahalliy ishlatish uchun)
load_dotenv()

# --- Maxfiy o'zgaruvchilar (Muhitdan olinadi) ---
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKENS_STR = os.environ.get("BOT_TOKENS", "")
BOT_TOKENS = BOT_TOKENS_STR.split(',') if BOT_TOKENS_STR else []

ADMIN_IDS_STR = os.environ.get("ADMIN_IDS", "")
ADMIN_IDS = [int(admin_id) for admin_id in ADMIN_IDS_STR.split(',')] if ADMIN_IDS_STR else []

NOTIFY_CHAT_ID = int(os.environ.get("NOTIFY_CHAT_ID", "0"))
UPGRADE_LIVE_CHAT_ID = int(os.environ.get("UPGRADE_LIVE_CHAT_ID", "0"))
SESSION_NAME = os.environ.get("SESSION_NAME", "account")


# --- Xavfsiz o'zgaruvchilar (Kodning o'zida qoladi) ---

# Render.com'dagi doimiy disk uchun yo'l
DATA_FILEPATH = Path("/data/star_gifts.json")
# Agar loyihani o'z kompyuteringizda ishga tushirmoqchi bo'lsangiz, yuqoridagi qatorni izohga oling (#)
# va quyidagi qatorni izohdan oching:
DATA_FILEPATH = constants.WORK_DIRPATH / "star_gifts.json"


# Boshqa sozlamalar
CHECK_INTERVAL = 1.0
UPGRADE_CHECK_INTERVAL = 1.0
DATA_SAVER_DELAY = 2.0
NOTIFY_AFTER_STICKER_DELAY = 1.0
NOTIFY_AFTER_TEXT_DELAY = 2.0
TIMEZONE = "UTC"
CONSOLE_LOG_LEVEL = logging.DEBUG
FILE_LOG_LEVEL = logging.INFO
HTTP_REQUEST_TIMEOUT = 20.0
COMMAND_PREFIX = "/"

# --- Xabar shablonlari ---

FOOTER_TEXT = """\


— — — — — — — — — — — — — — — —
<a href="https://t.me/crypto_click_games">Crypto Games</a> • <a href="https://t.me/portals/market?startapp=vtr1ow">Portals</a> • <a href="https://t.me/tonnel_network_bot/gifts?startapp=ref_1396503733">Tonnel</a> • <a href="https://t.me/TezUpgrade">TezUpgrade</a>"""

NOTIFY_TEXT = """\
{title}

№ {number} (<code>{id}</code>)
{total_amount}{available_amount}{sold_out}
💎 Narxi: {price} ⭐️
♻️ Konvertatsiya narxi: {convert_price} ⭐️{footer}
"""

NOTIFY_TEXT_TITLES = {True: "🔥 Yangi cheklangan sovg'a paydo bo'ldi", False: "❄️ Yangi sovg'a paydo bo'ldi"}

NOTIFY_TEXT_TOTAL_AMOUNT = "\n🎯 Umumiy soni: {total_amount}"
NOTIFY_TEXT_AVAILABLE_AMOUNT = "\n❓ Mavjud soni: {available_amount} ({same_str}{available_percentage}%, {updated_datetime} UTC da yangilandi)\n"
NOTIFY_TEXT_SOLD_OUT = "\n⏰ {sold_out} vaqt ichida to'liq sotildi\n"

NOTIFY_UPGRADE_LIVE_START_TEXT = "✅ `{gift_slug}` uchun kuzatuv boshlandi!{footer}"

NOTIFY_UPGRADE_LIVE_MESSAGE_FORMAT = """Upg ⬆️: <a href="https://t.me/nft/{gift_name}-{upgraded_id}">{gift_name}-{upgraded_id}</a>{footer}"""
