import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import constants

load_dotenv()

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKENS_STR = os.environ.get("BOT_TOKENS", "")
BOT_TOKENS = BOT_TOKENS_STR.split(',') if BOT_TOKENS_STR else []
ADMIN_IDS_STR = os.environ.get("ADMIN_IDS", "")
ADMIN_IDS = [int(admin_id) for admin_id in ADMIN_IDS_STR.split(',')] if ADMIN_IDS_STR else []
NOTIFY_CHAT_ID = int(os.environ.get("NOTIFY_CHAT_ID", "0"))
UPGRADE_LIVE_CHAT_ID = int(os.environ.get("UPGRADE_LIVE_CHAT_ID", "0"))
SESSION_NAME = os.environ.get("SESSION_NAME", "account")

DATA_FILEPATH = constants.WORK_DIRPATH / "star_gifts.json"
CHECK_INTERVAL = 1.0
UPGRADE_CHECK_INTERVAL = 1.0
DATA_SAVER_DELAY = 2.0
NOTIFY_AFTER_STICKER_DELAY = 1.0
NOTIFY_AFTER_TEXT_DELAY = 2.0
TIMEZONE = "UTC+5"
CONSOLE_LOG_LEVEL = logging.INFO
FILE_LOG_LEVEL = logging.INFO
HTTP_REQUEST_TIMEOUT = 20.0
COMMAND_PREFIX = "/"

FOOTER_TEXT = """\n\n— — — — — — — — — — — — — — — —\n<a href="https://t.me/crypto_click_games">Crypto Games</a> • <a href="https://t.me/portals/market?startapp=vtr1ow">Portals</a> • <a href="https://t.me/tonnel_network_bot/gifts?startapp=ref_1396503733">Tonnel</a> • <a href="https://t.me/TezUpgrade">TezUpgrade</a>"""
NOTIFY_TEXT = """{title}\n\n№ {number} (<code>{id}</code>){total_amount}{available_amount}{sold_out}\n\n💎 Narxi: {price} ⭐️\n♻️ Konvertatsiya narxi: {convert_price} ⭐️{footer}"""
NOTIFY_TEXT_TITLES = {True: "🔥 Yangi cheklangan sovg'a paydo bo'ldi", False: "❄️ Yangi sovg'a paydo bo'ldi"}
NOTIFY_TEXT_TOTAL_AMOUNT = "\n🎯 Umumiy soni: {total_amount}"
NOTIFY_TEXT_AVAILABLE_AMOUNT = "\n❓ Mavjud soni: {available_amount} ({same_str}{available_percentage}%, {updated_datetime} UTC+5 da yangilandi)"
NOTIFY_TEXT_SOLD_OUT = "\n⏰ {sold_out} vaqt ichida to'liq sotildi"
NOTIFY_UPGRADE_LIVE_START_TEXT = "✅ `{gift_slug}` uchun kuzatuv boshlandi!{footer}"
NOTIFY_UPGRADE_LIVE_MESSAGE_FORMAT = """Upg ⬆️: <a href="https://t.me/nft/{gift_name}-{upgraded_id}">{gift_name}-{upgraded_id}</a>{footer}"""
