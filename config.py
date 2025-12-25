from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        # Telegram API
        self.API_ID = int(getenv("API_ID", 0))
        self.API_HASH = getenv("API_HASH")
        self.BOT_TOKEN = getenv("BOT_TOKEN")
        
        # Database
        self.MONGO_URL = getenv("MONGO_URL")
        self.DB_NAME = getenv("DB_NAME", "DramaBot")
        
        # Owner & Logger
        self.LOGGER_ID = int(getenv("LOGGER_ID", 0))
        self.OWNER_ID = int(getenv("OWNER_ID", 0))
        
        # Queue Settings
        self.QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", 20))
        
        # Assistant Sessions
        self.SESSION1 = getenv("SESSION", None)
        self.SESSION2 = getenv("SESSION2", None)
        self.SESSION3 = getenv("SESSION3", None)
        
        # Playback Settings
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", True)
        
        # DramaBox API
        self.DRAMABOX_API_URL = getenv("DRAMABOX_API_URL", "https://dramabox.sansekai.my.id/api")
        
        # Images
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://te.legra.ph/file/3e40a408286d4eda24191.jpg")
        self.PING_IMG = getenv("PING_IMG", "https://files.catbox.moe/haagg2.png")
        self.START_IMG = getenv("START_IMG", "https://files.catbox.moe/zvziwk.jpg")
        self.BOT_BANNER = getenv("BOT_BANNER", self.START_IMG)

    def check(self):
        """Validate required environment variables"""
        required = ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URL", "LOGGER_ID", "OWNER_ID", "SESSION1"]
        missing = [var for var in required if not getattr(self, var)]
        
        if missing:
            raise SystemExit(f"❌ Missing required environment variables: {', '.join(missing)}")
