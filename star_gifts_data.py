from pydantic import BaseModel, Field
from pathlib import Path
import simplejson as json
import constants

class BaseConfigModel(BaseModel, extra="ignore"):
    pass

class StarGiftData(BaseConfigModel):
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

class StarGiftsData(BaseConfigModel):
    DATA_FILEPATH: Path = Field(exclude=True, default=None)
    notify_chat_id: int | None = Field(default=None)
    upgrade_live_chat_id: int | None = Field(default=None)
    star_gifts: list[StarGiftData] = Field(default_factory=list)

    @classmethod
    def load(cls, data_filepath: Path) -> "StarGiftsData":
        instance = cls()
        instance.DATA_FILEPATH = data_filepath
        try:
            with data_filepath.open("r", encoding=constants.ENCODING) as file:
                file_content = file.read()
                if not file_content:
                    return instance
                data = json.loads(file_content)
                return cls.model_validate({**data, "DATA_FILEPATH": data_filepath})
        except (FileNotFoundError, json.JSONDecodeError):
            return instance

    def save(self) -> None:
        with self.DATA_FILEPATH.open("w", encoding=constants.ENCODING) as file:
            json.dump(obj=self.model_dump(exclude={"DATA_FILEPATH"}), fp=file, indent=4, ensure_ascii=True, sort_keys=False)

