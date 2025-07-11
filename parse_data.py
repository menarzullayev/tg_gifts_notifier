from pyrogram import Client
from pyrogram.raw.types.payments.star_gifts import StarGifts
from pyrogram.raw.types.payments.star_gifts_not_modified import StarGiftsNotModified
from pyrogram.raw.functions.payments.get_star_gifts import GetStarGifts
from pyrogram.raw.functions.payments.get_star_gift_upgrade_preview import GetStarGiftUpgradePreview
from pyrogram.raw.types.star_gift import StarGift
from pyrogram.raw.types.document_attribute_filename import DocumentAttributeFilename
from pyrogram.file_id import FileId, FileType
from pyrogram.raw.types.payments.star_gift_upgrade_preview import StarGiftUpgradePreview




import utils
import typing

from star_gifts_data import StarGiftData


@typing.overload
async def get_all_star_gifts(
    client: Client,
    hash: typing.Literal[None] = ...
) -> tuple[int, dict[int, StarGiftData]]: ...

@typing.overload
async def get_all_star_gifts(
    client: Client,
    hash: int
) -> tuple[int, dict[int, StarGiftData] | None]: ...

async def get_all_star_gifts(
    client: Client,
    hash: int | None = None
) -> tuple[int, dict[int, StarGiftData] | None]:
    r = typing.cast(StarGifts | StarGiftsNotModified, await client.invoke(
        GetStarGifts(
            hash = hash or 0
        )
    ))

    if isinstance(r, StarGiftsNotModified):
        return (
            typing.cast(int, hash),
            None
        )

    r_gifts = typing.cast(list[StarGift], r.gifts)

    all_star_gifts_dict: dict[int, StarGiftData] = {
        star_gift_raw.id: StarGiftData(
            id = star_gift_raw.id,
            number = number,
            sticker_file_id = FileId(
                file_type = FileType.DOCUMENT,
                dc_id = typing.cast(int, star_gift_raw.sticker.dc_id),  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                media_id = typing.cast(int, star_gift_raw.sticker.id),  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                access_hash = typing.cast(int, star_gift_raw.sticker.access_hash),  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                file_reference = typing.cast(bytes, star_gift_raw.sticker.file_reference)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            ).encode(),
            sticker_file_name = next(
                (
                    attr.file_name
                    for attr in typing.cast(list[DocumentAttributeFilename | typing.Any], star_gift_raw.sticker.attributes)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                    if isinstance(attr, DocumentAttributeFilename)
                ),
                f"{star_gift_raw.id}.tgs"  # hardcode
            ),
            price = star_gift_raw.stars,
            convert_price = star_gift_raw.convert_stars,
            available_amount = star_gift_raw.availability_remains or 0,
            total_amount = star_gift_raw.availability_total or 0,
            is_limited = star_gift_raw.limited or False,
            first_appearance_timestamp = star_gift_raw.first_sale_date or utils.get_current_timestamp(),
            # channel_number_sent_to = None,
            last_sale_timestamp = star_gift_raw.last_sale_date
        )
        for number, star_gift_raw in enumerate(sorted(
            r_gifts,
            key = lambda star_gift_raw: star_gift_raw.id,
            reverse = False
        ), 1)
    }

    return (
        r.hash,
        all_star_gifts_dict
    )

async def get_upgrade_preview(app: Client, gift_id: int) -> StarGiftUpgradePreview | None:
    """
    Berilgan sovg'a uchun upgrade mavjudligini tekshiradi.

    Args:
        app: Pyrogram client'i.
        gift_id: Tekshirilayotgan sovg'aning ID'si.

    Returns:
        Agar yangi upgrade topilsa, StarGiftUpgradePreview obyektini, aks holda None qaytaradi.
    """
    try:
        # Telegram API ga so'rov yuborish
        return await app.invoke(
            GetStarGiftUpgradePreview(
                gift_id=gift_id
            )
        )
    except Exception:
        # Har qanday xatolik yuzaga kelsa, None qaytaramiz
        return None
