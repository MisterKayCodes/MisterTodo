import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Rule 3 & 11: Explicit imports to prevent Circular Dependency
from bot.handlers.commands import router as commands_router
from bot.handlers.callbacks import router as callbacks_router

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Rule 6: No smart guessing - exit if critical config is missing
if not TOKEN:
    print("CRITICAL: BOT_TOKEN not found in .env file.")
    sys.exit(1)

# Rule 10: Observability (Logs + Metrics)
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

# Rule 13: 2025 Standard - Fixed class initialization
bot = Bot(
    token=TOKEN, 
    default=DefaultBotProperties(parse_mode="HTML")
)

# Rule 18: Safe state storage (MemoryStorage for now)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- Router Registration ---
# Rule 5: Explicitly register separate routers to ensure Idempotency
dp.include_router(commands_router)
dp.include_router(callbacks_router)

async def main():
    # Rule 1: System starting in a known state
    logger.info("--- Starting Mister_Todo Engine (2025 Edition) ---")
    
    try:
        # Rule 18: Safe Deployment Protocol (Graceful Start)
        # Drop pending updates to avoid "spam" processing on restart
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        # Rule 12: Handle errors explicitly
        logger.critical(f"System crash detected: {e}", exc_info=True)
    finally:
        # Rule 7: Design for recovery/cleanup
        logger.info("System shutting down. Closing sessions...")
        await dp.storage.close()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Rule 18: Graceful Stop
        logger.info("Manually stopped by user.")
        sys.exit(0)

# Love From Mister
