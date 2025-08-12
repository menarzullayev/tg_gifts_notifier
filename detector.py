import os
import random
from pyrogram import Client, types
from httpx import AsyncClient, TimeoutException
from pytz import timezone as _timezone
from io import BytesIO
from itertools import cycle, groupby
from bisect import bisect_left
from functools import partial

import math
import asyncio
import typing

from parse_data import get_all_star_gifts
from star_gifts_data import StarGiftData, StarGiftsData

import utils
import constants
import config

from pyrogram import Client, types, filters


timezone = _timezone(config.TIMEZONE)

NULL_STR = ""


T = typing.TypeVar("T")
STAR_GIFT_RAW_T = dict[str, typing.Any]
UPDATE_GIFTS_QUEUE_T = asyncio.Queue[tuple[StarGiftData, StarGiftData]]



BOTS_AMOUNT = len(config.BOT_TOKENS)

if BOTS_AMOUNT > 0:
    BOT_HTTP_CLIENT = AsyncClient(base_url="https://api.telegram.org/", timeout=config.HTTP_REQUEST_TIMEOUT)

    BOT_TOKENS_CYCLE = cycle(config.BOT_TOKENS)


STAR_GIFTS_DATA = StarGiftsData.load(config.DATA_FILEPATH)
last_star_gifts_data_saved_time: int | None = None

logger = utils.get_logger(name=config.SESSION_NAME, log_filepath=constants.LOG_FILEPATH, console_log_level=config.CONSOLE_LOG_LEVEL, file_log_level=config.FILE_LOG_LEVEL)


@typing.overload
async def bot_send_request(method: str, data: dict[str, typing.Any] | None) -> dict[str, typing.Any]: ...


@typing.overload
async def bot_send_request(method: typing.Literal["editMessageText"], data: dict[str, typing.Any]) -> dict[str, typing.Any] | None: ...


async def bot_send_request(method: str, data: dict[str, typing.Any] | None = None) -> dict[str, typing.Any] | None:

    retries = BOTS_AMOUNT
    response = None

    for bot_token in BOT_TOKENS_CYCLE:
        retries -= 1

        if retries < 0:
            break

        try:
            response = (await BOT_HTTP_CLIENT.post(f"/bot{bot_token}/{method}", json=data)).json()

        except TimeoutException:
            logger.warning(f"Timeout exception while sending request {method} with data: {data}")

            continue

        if response.get("ok"):
            return response.get("result")

        elif method == "editMessageText" and isinstance(response.get("description"), str) and "message is not modified" in response["description"]:
            return

    raise RuntimeError(f"Failed to send request to Telegram API: {response}")


async def detector(app: Client, new_gift_callback: typing.Callable[[StarGiftData], typing.Coroutine[None, None, typing.Any]] | None = None, update_gifts_queue: UPDATE_GIFTS_QUEUE_T | None = None) -> None:
    if new_gift_callback is None and update_gifts_queue is None:
        raise ValueError("At least one of new_gift_callback or update_gifts_queue must be provided")

    # Birinchi marta ishga tushganda "boshlang'ich nuqta" yaratamiz
    if not STAR_GIFTS_DATA.star_gifts:
        logger.info("First run detected. Establishing baseline...")
        if not app.is_connected:
            await app.start()

        _, all_star_gifts_dict = await get_all_star_gifts(app)

        if all_star_gifts_dict:
            all_gifts_list = list(all_star_gifts_dict.values())

            # Barcha joriy sovg'alarni xabar yubormasdan bazaga saqlaymiz
            await star_gifts_data_saver(all_gifts_list)
            logger.info(f"Baseline established with {len(all_gifts_list)} gifts. Notifications will be sent only for new gifts.")

            # Test uchun 1 ta tasodifiy sovg'ani tanlab, xabar yuboramiz
            sample_size = min(1, len(all_gifts_list))
            if new_gift_callback and sample_size > 0:
                test_gifts = random.sample(all_gifts_list, sample_size)
                logger.info(f"Sending notifications for {len(test_gifts)} random gifts for testing purposes.")
                for star_gift in test_gifts:
                    await new_gift_callback(star_gift)

    # Asosiy kuzatuv sikli
    while True:
        if not app.is_connected:
            await app.start()

        _, all_star_gifts_dict = await get_all_star_gifts(app)

        old_star_gifts_dict = {star_gift.id: star_gift for star_gift in STAR_GIFTS_DATA.star_gifts}

        new_star_gifts = {star_gift_id: star_gift for star_gift_id, star_gift in all_star_gifts_dict.items() if star_gift_id not in old_star_gifts_dict}

        if new_star_gifts and new_gift_callback:
            logger.info(f"""Found {len(new_star_gifts)} new gifts: [{", ".join(map(str, new_star_gifts.keys()))}]""")
            for star_gift in new_star_gifts.values():
                await new_gift_callback(star_gift)

        if update_gifts_queue:
            for star_gift_id, old_star_gift in old_star_gifts_dict.items():
                new_star_gift = all_star_gifts_dict.get(star_gift_id)
                if new_star_gift is None:
                    logger.warning("Star gift not found in new gifts, skipping for updating", extra={"star_gift_id": str(star_gift_id)})
                    continue
                new_star_gift.message_id = old_star_gift.message_id
                if new_star_gift.available_amount < old_star_gift.available_amount:
                    update_gifts_queue.put_nowait((old_star_gift, new_star_gift))

        if new_star_gifts:
            await star_gifts_data_saver(list(new_star_gifts.values()))

        await asyncio.sleep(config.CHECK_INTERVAL)


def get_notify_text(star_gift: StarGiftData) -> str:
    is_limited = star_gift.is_limited

    available_percentage, available_percentage_is_same = (
        utils.pretty_float(math.ceil(star_gift.available_amount / star_gift.total_amount * 100 * 100) / 100, get_is_same=True)
        if is_limited and star_gift.total_amount > 0
        else (NULL_STR, False)
    )

    return config.NOTIFY_TEXT.format(
        title=config.NOTIFY_TEXT_TITLES[is_limited],
        number=star_gift.number,
        id=star_gift.id,
        total_amount=(config.NOTIFY_TEXT_TOTAL_AMOUNT.format(total_amount=utils.pretty_int(star_gift.total_amount)) if is_limited else NULL_STR),
        available_amount=(
            config.NOTIFY_TEXT_AVAILABLE_AMOUNT.format(
                available_amount=utils.pretty_int(star_gift.available_amount),
                same_str=("~" if not available_percentage_is_same else NULL_STR),
                available_percentage=available_percentage,
                updated_datetime=utils.get_current_datetime(timezone),
            )
            if is_limited
            else NULL_STR
        ),
        sold_out=(
            config.NOTIFY_TEXT_SOLD_OUT.format(sold_out=utils.format_seconds_to_human_readable(star_gift.last_sale_timestamp - star_gift.first_appearance_timestamp))
            if star_gift.last_sale_timestamp and star_gift.first_appearance_timestamp
            else NULL_STR
        ),
        price=utils.pretty_int(star_gift.price),
        convert_price=utils.pretty_int(star_gift.convert_price),
        footer=config.FOOTER_TEXT,
    )



async def process_new_gift(app: Client, star_gift: StarGiftData) -> None:
    reply_to_id = None
    try:
        binary = typing.cast(BytesIO, await app.download_media(message=star_gift.sticker_file_id, in_memory=True))
        binary.name = star_gift.sticker_file_name
        sticker_message = typing.cast(types.Message, await app.send_sticker(chat_id=STAR_GIFTS_DATA.notify_chat_id, sticker=binary))
        reply_to_id = sticker_message.id
    except Exception as e:
        logger.error(f"Stiker yuborishda xato ({star_gift.id}): {e}. Matn xabari stikersiz yuboriladi.")

    await asyncio.sleep(config.NOTIFY_AFTER_STICKER_DELAY)
    response = await bot_send_request(
        "sendMessage",
        {
            "chat_id": STAR_GIFTS_DATA.notify_chat_id,
            "text": get_notify_text(star_gift),
            "reply_to_message_id": reply_to_id,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
    )
    if response:
        star_gift.message_id = response.get("message_id")
        await star_gifts_data_saver(star_gift)


async def process_update_gifts(update_gifts_queue: UPDATE_GIFTS_QUEUE_T) -> None:
    while True:
        new_star_gifts: list[StarGiftData] = []

        while True:
            try:
                _, new_star_gift = update_gifts_queue.get_nowait()

                new_star_gifts.append(new_star_gift)

                update_gifts_queue.task_done()

            except asyncio.QueueEmpty:
                break

        if not new_star_gifts:
            await asyncio.sleep(0.1)

            continue

        new_star_gifts.sort(key=lambda star_gift: star_gift.id)

        for new_star_gift in [min(gifts, key=lambda star_gift: star_gift.available_amount) for _, gifts in groupby(new_star_gifts, key=lambda star_gift: star_gift.id)]:
            if new_star_gift.message_id is None:
                continue

            await bot_send_request(
                "editMessageText", {"chat_id": STAR_GIFTS_DATA.notify_chat_id, "message_id": new_star_gift.message_id, "text": get_notify_text(new_star_gift), "parse_mode": "HTML", "disable_web_page_preview": True}
            )
            logger.debug(f"Star gift updated with {new_star_gift.available_amount} available amount", extra={"star_gift_id": str(new_star_gift.id)})

        await star_gifts_data_saver(new_star_gifts)


star_gifts_data_saver_lock = asyncio.Lock()


async def star_gifts_data_saver(star_gifts: StarGiftData | list[StarGiftData]) -> None:
    global STAR_GIFTS_DATA, last_star_gifts_data_saved_time

    async with star_gifts_data_saver_lock:
        if not isinstance(star_gifts, list):
            star_gifts = [star_gifts]

        updated_gifts_list = list(STAR_GIFTS_DATA.star_gifts)

        for star_gift in star_gifts:
            pos = bisect_left([gift.id for gift in updated_gifts_list], star_gift.id)

            if pos < len(updated_gifts_list) and updated_gifts_list[pos].id == star_gift.id:
                updated_gifts_list[pos] = star_gift

            else:
                updated_gifts_list.insert(pos, star_gift)

        STAR_GIFTS_DATA.star_gifts = updated_gifts_list

        if last_star_gifts_data_saved_time is None or last_star_gifts_data_saved_time + config.DATA_SAVER_DELAY < utils.get_current_timestamp():
            STAR_GIFTS_DATA.save()

            last_star_gifts_data_saved_time = utils.get_current_timestamp()


async def find_last_upgrade_by_binary_search(slug: str, max_range: int = 1_000_000) -> int:
    """
    Binary Search algoritmi yordamida mavjud bo'lgan eng oxirgi upgrade raqamini topadi.
    """
    logger.info(f"`{slug}` uchun Binary Search orqali joriy upgrade soni qidirilmoqda...")
    low = 1
    high = max_range
    last_found = 0

    async with AsyncClient(timeout=10) as client:
        while low <= high:
            mid = (low + high) // 2
            if mid == 0:
                break

            url = f"https://t.me/nft/{slug}-{mid}"
            try:
                response = await client.get(url, follow_redirects=False)

                if response.status_code == 200:
                    # 'mid' raqami mavjud. Demak, bu raqam yoki undan kattaroqlari ham bo'lishi mumkin.
                    last_found = mid
                    low = mid + 1
                else:
                    # 'mid' raqami mavjud emas. Demak, oxirgi raqam quyi qismda.
                    high = mid - 1

                await asyncio.sleep(0.25)  # Serverga ortiqcha bosim o'tkazmaslik uchun

            except Exception as e:
                logger.warning(f"Binary search tekshiruvida xato ({url}): {e}")
                high = mid - 1  # Xatolik bo'lsa, bu diapazonni qisqartiramiz

    logger.info(f"`{slug}` uchun topilgan oxirgi raqam: {last_found}")
    return last_found


# --- YANGILANGAN FUNKSIYA ---
async def upgrade_live_tracker(app: Client) -> None:
    """
    Kuzatuvdagi sovg'alarni ommaviy asinxron so'rovlar ("batch") yordamida tekshiradi.
    """
    next_check_numbers = {}
    BATCH_SIZE = 15  # Bir vaqtda nechta ID tekshirilishini belgilaymiz

    # HTTP client'ni bir marta yaratib, butun sikl davomida qayta ishlatamiz
    async with AsyncClient(timeout=10) as client:
        while True:
            trackable_gifts = [g for g in STAR_GIFTS_DATA.star_gifts if g.is_upgradable and g.gift_slug]

            if not trackable_gifts:
                await asyncio.sleep(config.UPGRADE_CHECK_INTERVAL)
                continue

            for star_gift in trackable_gifts:
                # Agar bu sovg'a birinchi marta tekshirilayotgan bo'lsa, uning boshlang'ich raqamini o'rnatamiz
                if star_gift.gift_slug not in next_check_numbers:
                    start_num = star_gift.last_checked_upgrade_id or 0
                    next_check_numbers[star_gift.gift_slug] = start_num + 1

                # Agar topic hali ochilmagan bo'lsa, ochamiz
                if star_gift.live_topic_id is None:
                    try:
                        created_topic = await app.create_forum_topic(chat_id=STAR_GIFTS_DATA.upgrade_live_chat_id, title=star_gift.gift_slug)
                        star_gift.live_topic_id = created_topic.id
                        await bot_send_request("sendMessage", {"chat_id": STAR_GIFTS_DATA.upgrade_live_chat_id, "message_thread_id": star_gift.live_topic_id, "text": config.NOTIFY_UPGRADE_LIVE_START_TEXT.format(gift_slug=star_gift.gift_slug, footer=config.FOOTER_TEXT), "parse_mode": "HTML", "disable_web_page_preview": True})
                        await star_gifts_data_saver(star_gift)
                    except Exception as e:
                        logger.error(f"'{star_gift.gift_slug}' uchun topic yaratishda xato: {e}")
                        continue
                
                # --- YANGILANGAN MANTIQ: Ommaviy "SPRINT" SIKLI ---
                while True:  # Har bir sovg'a uchun bir nechta batch'ni tekshirish uchun sikl
                    start_num = next_check_numbers.get(star_gift.gift_slug, 1)
                    
                    numbers_to_check = list(range(start_num, start_num + BATCH_SIZE))
                    tasks = []
                    for number in numbers_to_check:
                        url = f"https://t.me/nft/{star_gift.gift_slug}-{number}"
                        tasks.append(client.get(url, follow_redirects=False))
                    
                    # Barcha so'rovlarni parallel ravishda yuboramiz
                    responses = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    found_count_in_batch = 0
                    last_found_in_batch = 0

                    for i, res in enumerate(responses):
                        current_check_num = numbers_to_check[i]
                        
                        # Xatolik yoki topilmagan holat
                        if isinstance(res, Exception) or res.status_code != 200:
                            # Agar birinchi elementdayoq xatolik bo'lsa, bu batchda hech narsa yo'q.
                            # Agar keyingi elementlarda xatolik bo'lsa, demak, shu yergacha bo'lganlar mavjud.
                            next_check_numbers[star_gift.gift_slug] = current_check_num
                            break  # Bu batch'ni tekshirishni to'xtatamiz

                        # Muvaffaqiyatli topildi
                        found_count_in_batch += 1
                        last_found_in_batch = current_check_num
                        logger.info(f"[+] TOPILDI (BATCH): {star_gift.gift_slug}-{current_check_num}")
                        
                        final_gift_name = star_gift.gift_slug or str(star_gift.id)
                        
                        # Xabar yuborish
                        await bot_send_request("sendMessage", {
                            "chat_id": STAR_GIFTS_DATA.upgrade_live_chat_id, 
                            "message_thread_id": star_gift.live_topic_id, 
                            "text": config.NOTIFY_UPGRADE_LIVE_MESSAGE_FORMAT.format(gift_name=final_gift_name, upgraded_id=current_check_num, footer=config.FOOTER_TEXT), 
                            "parse_mode": "HTML", 
                            "disable_web_page_preview": False
                        })
                        
                        # Kichik pauza, Telegram API'ga bosimni kamaytirish uchun
                        await asyncio.sleep(0.1) 

                    # Agar batch'da biror nima topilgan bo'lsa, ma'lumotni saqlaymiz
                    if last_found_in_batch > 0:
                        star_gift.last_checked_upgrade_id = last_found_in_batch
                        await star_gifts_data_saver(star_gift)

                    # Agar batch to'liq muvaffaqiyatli bo'lmagan bo'lsa (oxiriga yetdik)
                    if found_count_in_batch < BATCH_SIZE:
                        break  # Keyingi sovg'aga o'tish uchun batch siklidan chiqamiz
                    else:
                        # Batch to'liq topildi, keyingi batch'ga tayyorlanamiz
                        next_check_numbers[star_gift.gift_slug] = start_num + BATCH_SIZE

            # Barcha sovg'alarni bir aylanib chiqqandan so'ng umumiy pauza
            await asyncio.sleep(config.UPGRADE_CHECK_INTERVAL)


async def logger_wrapper(coro: typing.Awaitable[T]) -> T | None:
    try:
        return await coro
    except Exception as ex:
        logger.exception(f"""Error in {getattr(coro, "__name__", coro)}: {ex}""")


async def main() -> None:
    logger.info("Starting gifts detector...")

    app = Client(
        name=config.SESSION_NAME,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        workdir=os.getcwd()
    )

    # --- Barcha buyruq handerlarini shu yerga yig'amiz ---
    @app.on_message(filters.command("addnew", prefixes=config.COMMAND_PREFIX) & filters.user(config.ADMIN_IDS))
    async def handle_add_new_command(client: Client, message: types.Message):
        try:
            if len(message.command) != 3: raise ValueError
            new_gift_slug, new_gift_id = message.command[1], int(message.command[2])
            target_gift = next((g for g in STAR_GIFTS_DATA.star_gifts if g.id == new_gift_id), None)

            await message.reply_text(f"`{new_gift_slug}` uchun joriy 'upgrade' soni Binary Search orqali qidirilmoqda...")
            last_upgrade_num = await find_last_upgrade_by_binary_search(new_gift_slug)

            if target_gift:
                logger.info(f"Mavjud sovg'a ({new_gift_id}) 'Live Upgrade' kuzatuviga sozlanmoqda.")
                target_gift.gift_slug, target_gift.is_upgradable, target_gift.live_topic_id, target_gift.last_checked_upgrade_id = new_gift_slug, True, None, last_upgrade_num
                await star_gifts_data_saver(target_gift)
                await message.reply_text(f"✅ **Mavjud sovg'a yangilandi!**\n\n**To'plam:** `{new_gift_slug}`\n**Topilgan joriy soni:** `{last_upgrade_num}`\n\nKuzatuv **#{last_upgrade_num + 1}**-raqamdan boshlanadi.")
            else:
                logger.info(f"Yangi sovg'a to'plami ({new_gift_slug}) bazaga qo'shilmoqda.")
                new_gift = StarGiftData(id=new_gift_id, number=999, sticker_file_id="placeholder", sticker_file_name=f"{new_gift_slug}.tgs", price=0, convert_price=0, available_amount=1, total_amount=1, is_limited=True, gift_slug=new_gift_slug, is_upgradable=True, live_topic_id=None, last_checked_upgrade_id=last_upgrade_num)
                await star_gifts_data_saver(new_gift)
                await message.reply_text(f"✅ **Yangi sovg'a qo'shildi!**\n\n**To'plam:** `{new_gift_slug}`\n**Topilgan joriy soni:** `{last_upgrade_num}`\n\nKuzatuv **#{last_upgrade_num + 1}**-raqamdan boshlanadi.")
        except (IndexError, ValueError):
            await message.reply_text("❌ Xatolik: `/addnew <nom> <bitta_ID>`\nMasalan: `/addnew SnoopDogg 901234567890`")

    @app.on_message(filters.command("setchat", prefixes=config.COMMAND_PREFIX) & filters.user(config.ADMIN_IDS))
    async def handle_set_chat_id(client: Client, message: types.Message):
        try:
            new_id = int(message.command[1])
            STAR_GIFTS_DATA.notify_chat_id = new_id
            STAR_GIFTS_DATA.save()
            await message.reply_text(f"✅ Yangi sovg'alar kanali ID'si o'rnatildi: `{new_id}`")
        except (IndexError, ValueError):
            await message.reply_text("❌ Xatolik: `/setchat <chat_id>`")

    @app.on_message(filters.command("setlivechat", prefixes=config.COMMAND_PREFIX) & filters.user(config.ADMIN_IDS))
    async def handle_set_live_chat_id(client: Client, message: types.Message):
        try:
            new_id = int(message.command[1])
            STAR_GIFTS_DATA.upgrade_live_chat_id = new_id
            STAR_GIFTS_DATA.save()
            await message.reply_text(f"✅ 'Live Upgrade' guruhi ID'si o'rnatildi: `{new_id}`")
        except (IndexError, ValueError):
            await message.reply_text("❌ Xatolik: `/setlivechat <chat_id>`")

    # --- Asosiy dastur mantig'i ---
    async with app:
        # Saqlangan sozlamalarni o'qiymiz yoki standart qiymatlarni o'rnatamiz
        if STAR_GIFTS_DATA.notify_chat_id is None:
            STAR_GIFTS_DATA.notify_chat_id = config.NOTIFY_CHAT_ID
        if STAR_GIFTS_DATA.upgrade_live_chat_id is None:
            STAR_GIFTS_DATA.upgrade_live_chat_id = config.UPGRADE_LIVE_CHAT_ID

        tasks = []
        update_gifts_queue = UPDATE_GIFTS_QUEUE_T() if BOTS_AMOUNT > 0 else None
        if update_gifts_queue:
            tasks.append(asyncio.create_task(logger_wrapper(process_update_gifts(update_gifts_queue))))
        else:
            logger.info("No bots available, skipping update gifts processing")

        if STAR_GIFTS_DATA.upgrade_live_chat_id:
            tasks.append(asyncio.create_task(logger_wrapper(upgrade_live_tracker(app))))
        else:
            logger.info("Upgrade Live channel is not set, skipping star gifts live upgrades tracking")

        tasks.append(asyncio.create_task(logger_wrapper(detector(app, new_gift_callback=partial(process_new_gift, app), update_gifts_queue=update_gifts_queue))))

        logger.info("Bot is running... All tasks started.")
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    finally:
        if STAR_GIFTS_DATA.star_gifts or STAR_GIFTS_DATA.notify_chat_id is not None:
            STAR_GIFTS_DATA.save()
            logger.info("Final data saved. Exiting.")
