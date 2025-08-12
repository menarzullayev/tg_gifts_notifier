from pydantic import BaseModel, Field

# Bu klass faqat ma'lumotlar tuzilishini aniqlash uchun ishlatiladi
class StarGiftData(BaseModel, extra="ignore"):
    id: int
    number: int
    sticker_file_id: str
    sticker_file_name: str
    price: int
    convert_price: int
    available_amount: int
    total_amount: int
    is_limited: bool
    first_appearance_timestamp: int | None = Field(default=None)
    message_id: int | None = Field(default=None)
    last_sale_timestamp: int | None = Field(default=None)
    is_upgradable: bool = Field(default=False)
    last_checked_upgrade_id: int | None = Field(default=None)
    live_topic_id: int | None = Field(default=None)
    gift_slug: str | None = Field(default=None)
