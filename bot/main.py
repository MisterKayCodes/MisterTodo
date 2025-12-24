import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from bot.handlers import commands

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("CRITICAL: BOT_TOKEN not found in .env file.")
    sys.exit(1)

LOG_FILE = "storage/logs/bot.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(commands.router)

async def main():
    logger.info("--- Starting Mister_Todo Engine (2025 Edition) ---")
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"System crash detected: {e}", exc_info=True)
    finally:
        logger.info("System shutting down. Closing sessions...")
        await dp.storage.close()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Manually stopped by user.")
        sys.exit(0)

# Love From Mister
