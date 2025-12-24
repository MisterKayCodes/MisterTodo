import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters.command import Command

# 1. Load & Validate Environment (Rule 6 & Rule 14)
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("CRITICAL: TELEGRAM_BOT_TOKEN not found in .env file.")
    sys.exit(1)

# 2. Ensure required directories exist (logs, db, backups)
os.makedirs("storage/logs", exist_ok=True)
os.makedirs("storage/db", exist_ok=True)
os.makedirs("storage/backups", exist_ok=True)

# 3. Setup Advanced Logging (Rule 10)
LOG_FILE = "storage/logs/bot.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)  # Console output too
    ]
)
logger = logging.getLogger(__name__)

# 4. Initialize Bot and Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 5. Simple Handler (Temporary for Task 1.2)
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Hello! Mister_Todo is up and running.")

# 6. The Main Loop (Rule 1, 7, 12)
async def main():
    logger.info("--- Starting Mister_Todo Engine (2025 Edition) ---")
    
    try:
        # Idempotency: clear webhook and pending updates before polling (Rule 5)
        await bot.delete_webhook(drop_pending_updates=True)
        
        logger.info("Bot started. Polling for updates...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.critical(f"System crash detected: {e}", exc_info=True)
    finally:
        logger.info("System shutting down. Closing bot session...")
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Manually stopped by user.")
        sys.exit(0)

# Love From Mister
