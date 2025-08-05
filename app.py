"""
Файл для запуска парсера без бота (тестирование)
"""
from src.parser import WildberriesReviewParser
from config.settings import PRODUCT_URL

def main():
    parser = WildberriesReviewParser()
    parser.parse_reviews(PRODUCT_URL)

if __name__ == "__main__":
    main()