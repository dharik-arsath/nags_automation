from telegram import Bot
from tenacity import retry, wait_exponential
from loguru import logger
from telegram.request import HTTPXRequest

from dotenv import load_dotenv


import os

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

trequest = HTTPXRequest(connection_pool_size=20)


@retry(wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True)
async def _send_message(id: str, msg: str):
    bot = Bot(BOT_TOKEN, request=trequest)
    try:
        async with bot:
            resp = await bot.send_message(id, msg, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Exception in send_message: {e}")
        raise e

    return resp


@retry(wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True)
async def _send_photo(id: str, photo: str):
    bot = Bot(BOT_TOKEN, request=trequest)
    try:
        async with bot:
            with open(photo, "rb") as file:
                resp = await bot.send_photo(id, photo=file)
    except Exception as e:
        logger.error(f"Exception in send_message: {e}")
        raise e

    return resp


async def send_message(msg: str):
    resp = await _send_message(CHANNEL_ID, msg)
    return resp


async def send_photo(photo: str):
    resp = await _send_photo(CHANNEL_ID, photo)
    return resp


if __name__ == "__main__":
    # asyncio.run(send_message("hi from python"))
    pass
