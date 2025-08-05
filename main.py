"""
Главный файл для запуска Telegram бота
"""
import asyncio
from bot.bot_manager import run_bot

def main():
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()