"""
Парсер отзывов Wildberries
"""
import re
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime

from config.settings import (
    MAX_REVIEWS, 
    MAX_VALUATION, 
    CARD_API_BASE_URL,
    FEEDBACKS_API_BASE_URL, 
    REQUEST_TIMEOUT, 
    REQUEST_HEADERS
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WildberriesReviewParser:
    """Парсер отзывов с Wildberries"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
    
    def extract_article_from_url(self, product_url: str) -> Optional[str]:
        """Извлекает артикул товара из URL"""
        pattern = r'/catalog/(\d+)/'
        match = re.search(pattern, product_url)
        return match.group(1) if match else None
    
    def fetch_product_root_id(self, article: str) -> Optional[str]:
        """Получает root ID товара из API карточки"""
        try:
            url = f"{CARD_API_BASE_URL}{article}"
            logger.info(f"Запрос к API карточки товара: {url}")
            
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            products = data.get('data', {}).get('products', [])
            
            if not products:
                logger.error("Товар не найден в ответе API")
                return None
                
            root_id = products[0].get('root')
            if not root_id:
                logger.error("Root ID не найден в данных товара")
                return None
                
            logger.info(f"Root ID товара: {root_id}")
            return str(root_id)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к API карточки: {e}")
            return None
        except ValueError as e:
            logger.error(f"Ошибка при парсинге JSON карточки: {e}")
            return None
    
    def fetch_reviews_data(self, root_id: str) -> Optional[Dict]:
        """Получает данные отзывов по root ID товара"""
        try:
            url = f"{FEEDBACKS_API_BASE_URL}{root_id}"
            logger.info(f"Запрос к API отзывов: {url}")
            
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к API отзывов: {e}")
            return None
        except ValueError as e:
            logger.error(f"Ошибка при парсинге JSON отзывов: {e}")
            return None
    
    def filter_reviews_with_content(self, reviews: List[Dict]) -> List[Dict]:
        """Фильтрует отзывы, содержащие текст в полях text, pros или cons"""
        filtered_reviews = []
        
        for review in reviews:
            has_content = (
                (review.get('text', '').strip()) or 
                (review.get('pros', '').strip()) or 
                (review.get('cons', '').strip())
            )
            
            if has_content:
                filtered_reviews.append(review)
        
        return filtered_reviews
    
    def get_latest_reviews(self, reviews: List[Dict], limit: int = MAX_REVIEWS) -> List[Dict]:
        """Получает последние отзывы по времени создания"""
        # Сортируем по дате создания (убывание)
        sorted_reviews = sorted(
            reviews, 
            key=lambda x: x.get('createdDate', ''), 
            reverse=True
        )
        
        return sorted_reviews[:limit]
    
    def filter_low_rating_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """Фильтрует отзывы с низкой оценкой (меньше MAX_VALUATION)"""
        return [
            review for review in reviews 
            if review.get('productValuation', 5) <= MAX_VALUATION
        ]
    
    def format_review_for_log(self, review: Dict) -> str:
        """Форматирует отзыв для вывода в лог"""
        user_name = review.get('wbUserDetails', {}).get('name', 'Аноним')
        rating = review.get('productValuation', 'Не указано')
        created_date = review.get('createdDate', '')
        
        # Форматируем дату
        try:
            date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%d.%m.%Y %H:%M')
        except:
            formatted_date = created_date
        
        text = review.get('text', '').strip()
        pros = review.get('pros', '').strip()
        cons = review.get('cons', '').strip()
        
        review_content = []
        if text:
            review_content.append(f"Текст: {text}")
        if pros:
            review_content.append(f"Плюсы: {pros}")
        if cons:
            review_content.append(f"Минусы: {cons}")
        
        content = " | ".join(review_content)
        
        return f"[{formatted_date}] {user_name} (Оценка: {rating}): {content}"
    
    def parse_reviews(self, product_url: str) -> None:
        """Основной метод парсинга отзывов"""
        logger.info(f"Начинаем парсинг отзывов для товара: {product_url}")
        
        # Извлекаем артикул из URL
        article = self.extract_article_from_url(product_url)
        if not article:
            logger.error("Не удалось извлечь артикул из URL")
            return
        
        logger.info(f"Артикул товара: {article}")
        
        # Получаем root ID товара
        root_id = self.fetch_product_root_id(article)
        if not root_id:
            logger.error("Не удалось получить root ID товара")
            return
        
        # Получаем данные отзывов по root ID
        data = self.fetch_reviews_data(root_id)
        if not data:
            logger.error("Не удалось получить данные отзывов")
            return
        
        reviews = data.get('feedbacks', [])
        if not reviews:
            logger.info("Отзывы не найдены")
            return
        
        logger.info(f"Всего отзывов получено: {len(reviews)}")
        
        # Фильтруем отзывы с содержимым
        reviews_with_content = self.filter_reviews_with_content(reviews)
        logger.info(f"Отзывов с содержимым: {len(reviews_with_content)}")
        
        # Получаем последние отзывы
        latest_reviews = self.get_latest_reviews(reviews_with_content)
        logger.info(f"Последних отзывов для анализа: {len(latest_reviews)}")
        
        # Фильтруем отзывы с низкой оценкой
        low_rating_reviews = self.filter_low_rating_reviews(latest_reviews)
        
        if not low_rating_reviews:
            logger.info(f"Отзывов с оценкой меньше {MAX_VALUATION} не найдено среди последних {MAX_REVIEWS}")
            return
        
        logger.info(f"Найдено {len(low_rating_reviews)} отзывов с оценкой меньше {MAX_VALUATION}:")
        logger.info("=" * 80)
        
        for i, review in enumerate(low_rating_reviews, 1):
            formatted_review = self.format_review_for_log(review)
            logger.info(f"{i}. {formatted_review}")
            logger.info("-" * 80)