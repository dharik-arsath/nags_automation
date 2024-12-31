import asyncio
from telegram import Bot 
from tenacity import retry,wait_exponential
from loguru import logger

from dotenv import load_dotenv

import os 

load_dotenv()
BOT_TOKEN  = os.environ.get("BOT_TOKEN")
CHAT_ID    = os.environ.get("CHAT_ID")
CHANNEL_ID = os.environ.get("CHANNEL_ID") 

bot = Bot(BOT_TOKEN)

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True)
async def send_message(id: str, msg: str):
    try:
        resp = await bot.send_message(id, msg)
    except Exception as e:
        logger.error(f"Exception in send_message: {e}") 
        raise e 
    
    return resp 

async def main():
    text = "Hi From Python"
    resp = await send_message(CHANNEL_ID, text)
    print(resp)
    return 

if __name__ == "__main__":
    asyncio.run(main())