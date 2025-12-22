# Copyright (c) 2025 DramaBot
# Bot untuk streaming drama ke Telegram voice chat
# Powered by DramaBox API


import time
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=10485760, backupCount=5),
        logging.StreamHandler(),
    ],
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("ntgcalls").setLevel(logging.CRITICAL)
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


__version__ = "1.0.0"

from config import Config

config = Config()
config.check()
tasks = []
boot = time.time()

from drama.core.bot import Bot
app = Bot()

from drama.core.dir import ensure_dirs
ensure_dirs()

from drama.core.userbot import Userbot
userbot = Userbot()

from drama.core.mongo import MongoDB
db = MongoDB()

from drama.core.telegram import Telegram
tg = Telegram()

from drama.api import DramaBoxAPI
api = DramaBoxAPI()

from drama.helpers import Queue
queue = Queue()

from drama.core.calls import TgCall
drama_call = TgCall()


async def stop() -> None:
    logger.info("Stopping...")
    for task in tasks:
        task.cancel()
        try:
            await task
        except:
            pass

    await app.exit()
    await userbot.exit()
    await db.close()
    await api.close()

    logger.info("Stopped.\n")

