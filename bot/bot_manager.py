import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import BOT_TOKEN
from bot.handlers import router

class BotManager:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.dp.include_router(router)
    
    async def start(self):
        logging.basicConfig(level=logging.INFO)
        logging.info("Запуск Telegram бота...")
        await self.dp.start_polling(self.bot)

async def run_bot():
    bot_manager = BotManager()
    await bot_manager.start()