# Конфигурация парсера отзывов Wildberries

# Максимальное количество отзывов для обработки
MAX_REVIEWS = 5

# Максимальная оценка для фильтрации (показываем отзывы с оценкой меньше этого значения)
MAX_VALUATION = 3

# URL товара для парсинга (пример)
PRODUCT_URL = "https://www.wildberries.ru/catalog/44587938/detail.aspx"

# Базовый URL для API карточки товара
CARD_API_BASE_URL = "https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-59202&spp=30&ab_testing=false&nm="

# Базовый URL для API отзывов
FEEDBACKS_API_BASE_URL = "https://feedbacks1.wb.ru/feedbacks/v2/"

# Настройки запросов
REQUEST_TIMEOUT = 10
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Настройки Telegram бота
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", 0))