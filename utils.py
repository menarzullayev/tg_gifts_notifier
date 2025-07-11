from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime, tzinfo

import logging
import numpy as np
import time
import typing


class StrippingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.msg = record.msg.strip() if isinstance(record.msg, str) else record.msg

        return super().format(record)


def get_logger(name: str, log_filepath: Path, console_log_level: int=logging.INFO, file_log_level: int=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)

    logger.setLevel(min(console_log_level, file_log_level))

    formatter = StrippingFormatter("%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        filename = log_filepath.resolve().as_posix(),
        mode = "a",
        maxBytes = 1028 * 1024,  # 1 MB
        backupCount = 1_000,
        encoding = "utf-8"
    )

    file_handler.setLevel(file_log_level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_current_datetime(timezone: tzinfo) -> str:
    return datetime.now(tz=timezone).strftime("%d-%m-%Y %H:%M:%S")

def get_current_timestamp() -> int:
    return int(time.time())


def pretty_int(number: int) -> str:
    return "{:,}".format(number)


@typing.overload
def pretty_float(number: float, get_is_same: typing.Literal[True]) -> tuple[str, bool]: ...

@typing.overload
def pretty_float(number: float, get_is_same: typing.Literal[False]) -> str: ...

def pretty_float(number: float, get_is_same: bool=False) -> tuple[str, bool] | str:
    formatted_number = float("{:.1g}".format(float(number)))
    formatted_number_str = np.format_float_positional(formatted_number, trim="-")

    if get_is_same:
        return (
            formatted_number_str,
            formatted_number == number
        )

    return formatted_number_str


def format_seconds_to_human_readable(total_seconds: int) -> str:
    total_seconds = int(total_seconds)

    if total_seconds < 0:
        total_seconds = 0

    days = total_seconds // (24 * 3600)
    total_seconds %= (24 * 3600)
    hours = total_seconds // 3600
    total_seconds %= 3600
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    parts: list[str] = []

    if days > 0:
        parts.append(f"{days} kun" + ("s" if days != 1 else ""))
    if hours > 0:
        parts.append(f"{hours} soat" + ("s" if hours != 1 else ""))
    if minutes > 0:
        parts.append(f"{minutes} daqiqa" + ("s" if minutes != 1 else ""))

    if seconds > 0 or (not parts and total_seconds == 0):
        parts.append(f"{seconds} soniya" + ("s" if seconds != 1 else ""))

    if not parts:
        return "0 soniya"

    elif len(parts) == 1:
        return parts[0]

    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"

    return ", ".join(parts[:-1]) + f" and {parts[-1]}"
