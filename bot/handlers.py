from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards import (
    get_main_keyboard, get_settings_keyboard, get_links_keyboard, 
    get_back_keyboard, get_add_links_inline_keyboard, get_delete_confirmation_keyboard
)
from bot.enums import Commands, ButtonTexts, Messages, Emojis, CallbackData
from src.parser import WildberriesReviewParser
from config.settings import TELEGRAM_USER_ID
from db.database import Database

router = Router()

class ParsingStates(StatesGroup):
    waiting_for_url = State()

class LinkStates(StatesGroup):
    adding_links = State()
    deleting_links = State()

db = Database()

def check_user_access(user_id: int) -> bool:
    return user_id == TELEGRAM_USER_ID

@router.message(Command(Commands.START))
async def start_handler(message: Message):
    if not check_user_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED)
        return
    
    await message.answer(Messages.WELCOME, reply_markup=get_main_keyboard())

# Главное меню
@router.message(F.text == ButtonTexts.PARSE_REVIEWS)
async def parse_button_handler(message: Message, state: FSMContext):
    if not check_user_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED_SHORT)
        return
    
    urls = await db.get_all_urls()
    if not urls:
        await message.answer(Messages.NO_SAVED_LINKS_ADD, reply_markup=get_main_keyboard())
        return
    
    await message.answer(Messages.PARSING_ALL_LINKS)
    
    for article, url in urls:
        try:
            parser = WildberriesReviewParser()
            result = await parse_reviews_async(parser, url)
            
            # Отправляем сообщение для каждого артикула независимо от результата
            response = format_article_reviews_response(article, result)
            await message.answer(response)
            
        except Exception as e:
            await message.answer(Messages.PARSING_ERROR_ARTICLE.format(article=article, error=str(e)))
    
    await message.answer(Messages.PARSING_COMPLETED, reply_markup=get_main_keyboard())

@router.message(F.text == ButtonTexts.SETTINGS)
async def settings_handler(message: Message):
    if not check_user_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED_SHORT)
        return
    
    await message.answer(Messages.SETTINGS_MENU, reply_markup=get_settings_keyboard())

@router.message(F.text == ButtonTexts.MAIN_MENU)
async def main_menu_handler(message: Message, state: FSMContext):
    if not check_user_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED_SHORT)
        return
    
    await state.clear()
    await message.answer(Messages.MAIN_MENU_TEXT, reply_markup=get_main_keyboard())

# Управление ссылками
@router.message(F.text == ButtonTexts.LINKS)
async def links_handler(message: Message):
    if not check_user_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED_SHORT)
        return
    
    count = await db.get_urls_count()
    await message.answer(Messages.LINKS_MANAGEMENT.format(count=count), reply_markup=get_links_keyboard())

@router.message(F.text == ButtonTexts.SHOW_ALL_LINKS)
async def show_all_links_handler(message: Message):
    if not check_user_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED_SHORT)
        return
    
    urls = await db.get_all_urls()
    if not urls:
        await message.answer(Messages.NO_SAVED_LINKS)
        return
    
    response = Messages.SAVED_LINKS_LIST
    for i, (article, url) in enumerate(urls, 1):
        response += f"{i}. {article}\n{url}\n\n"
    
    await message.answer(response)

@router.message(F.text == ButtonTexts.ADD_LINK)
async def add_link_handler(message: Message, state: FSMContext):
    if not check_user_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED_SHORT)
        return
    
    count = await db.get_urls_count()
    if count >= 30:
        await message.answer(Messages.LINKS_LIMIT_REACHED)
        return
    
    await message.answer(Messages.SEND_LINKS, reply_markup=get_back_keyboard())
    await state.set_state(LinkStates.adding_links)
    await state.update_data(pending_links=[])

@router.message(StateFilter(LinkStates.adding_links))
async def add_links_handler(message: Message, state: FSMContext):
    if not check_user_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED_SHORT)
        await state.clear()
        return
    
    if message.text == ButtonTexts.BACK:
        await state.clear()
        await message.answer(Messages.LINKS_MANAGEMENT.format(count=await db.get_urls_count()), reply_markup=get_links_keyboard())
        return
    
    data = await state.get_data()
    pending_links = data.get('pending_links', [])
    
    # Ищем все ссылки в тексте (могут быть разделены пробелами, переносами строк и т.д.)
    import re
    url_pattern = r'https://www\.wildberries\.ru/catalog/\d+/detail\.aspx'
    found_urls = re.findall(url_pattern, message.text)
    
    valid_urls = []
    parser = WildberriesReviewParser()
    
    # Получаем существующие артикулы из БД
    existing_urls = await db.get_all_urls()
    existing_articles = {article for article, _ in existing_urls}
    
    # Создаем множество для отслеживания уже обработанных артикулов в текущем сообщении
    processed_articles = set()
    
    for url in found_urls:
        article = parser.extract_article_from_url(url)
        if article:
            # Проверяем все возможные дубликаты:
            # 1. Не существует в БД
            # 2. Не добавлен в предыдущих сессиях (pending_links)
            # 3. Не обработан в текущем сообщении
            if (article not in existing_articles and 
                not any(existing_article == article for existing_article, _ in pending_links) and
                article not in processed_articles):
                valid_urls.append((article, url))
                processed_articles.add(article)
    
    if not valid_urls:
        if found_urls:
            await message.answer("Все найденные ссылки уже добавлены или некорректны.")
        else:
            await message.answer(Messages.NO_VALID_LINKS)
        return
    
    pending_links.extend(valid_urls)
    await state.update_data(pending_links=pending_links)
    
    # Информируем о найденных ссылках
    if len(found_urls) > len(valid_urls):
        skipped = len(found_urls) - len(valid_urls)
        
        # Подсчитываем типы пропущенных ссылок
        duplicates_in_db = 0
        duplicates_in_session = 0
        duplicates_in_message = 0
        
        processed_in_message = set()
        for url in found_urls:
            article = parser.extract_article_from_url(url)
            if article:
                if article in existing_articles:
                    duplicates_in_db += 1
                elif any(existing_article == article for existing_article, _ in pending_links):
                    duplicates_in_session += 1
                elif article in processed_in_message:
                    duplicates_in_message += 1
                else:
                    processed_in_message.add(article)
        
        skip_reasons = []
        if duplicates_in_db > 0:
            skip_reasons.append(f"{duplicates_in_db} уже в БД")
        if duplicates_in_session > 0:
            skip_reasons.append(f"{duplicates_in_session} уже в сессии")
        if duplicates_in_message > 0:
            skip_reasons.append(f"{duplicates_in_message} дубликаты в сообщении")
        
        reason_text = ", ".join(skip_reasons) if skip_reasons else "некорректные"
        await message.answer(f"Найдено {len(found_urls)} ссылок, добавлено {len(valid_urls)} новых. Пропущено {skipped} ({reason_text}).")
    
    # Проверяем лимит после добавления новых ссылок
    current_count = await db.get_urls_count()
    total_after_adding = current_count + len(pending_links)
    
    if total_after_adding > 30:
        available = 30 - current_count
        if available <= 0:
            await message.answer(Messages.LINKS_LIMIT_REACHED)
            return
        else:
            # Обрезаем список до доступного лимита
            pending_links = pending_links[:available]
            await state.update_data(pending_links=pending_links)
            await message.answer(f"Можно добавить только {available} ссылок из {len(valid_urls)} найденных.")
    
    articles = [article for article, _ in pending_links]
    await message.answer(
        Messages.CONFIRM_ADD_LINKS.format(count=len(pending_links)) + 
        "\n".join(f"{i+1}. {article}" for i, article in enumerate(articles)),
        reply_markup=get_add_links_inline_keyboard()
    )

@router.message(F.text == ButtonTexts.DELETE_LINK)
async def delete_link_handler(message: Message, state: FSMContext):
    if not check_user_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED_SHORT)
        return
    
    urls = await db.get_all_urls()
    if not urls:
        await message.answer(Messages.NO_LINKS_TO_DELETE)
        return
    
    response = Messages.DELETE_INSTRUCTIONS
    for i, (article, _) in enumerate(urls, 1):
        response += f"{i}. {article}\n"
    
    await message.answer(response, reply_markup=get_back_keyboard())
    await state.set_state(LinkStates.deleting_links)
    await state.update_data(all_urls=urls)

@router.message(StateFilter(LinkStates.deleting_links))
async def delete_links_handler(message: Message, state: FSMContext):
    if not check_user_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED_SHORT)
        await state.clear()
        return
    
    if message.text == ButtonTexts.BACK:
        await state.clear()
        await message.answer(Messages.LINKS_MANAGEMENT.format(count=await db.get_urls_count()), reply_markup=get_links_keyboard())
        return
    
    data = await state.get_data()
    all_urls = data.get('all_urls', [])
    
    input_text = message.text.strip()
    items = [item.strip() for item in input_text.split(',')]
    
    articles_to_delete = []
    
    for item in items:
        if item.isdigit():
            index = int(item) - 1
            if 0 <= index < len(all_urls):
                articles_to_delete.append(all_urls[index][0])
        else:
            for article, _ in all_urls:
                if article == item:
                    articles_to_delete.append(article)
                    break
    
    if not articles_to_delete:
        await message.answer(Messages.NO_MATCHING_LINKS)
        return
    
    await state.update_data(articles_to_delete=articles_to_delete)
    await message.answer(
        Messages.CONFIRM_DELETE_LINKS + "\n".join(articles_to_delete),
        reply_markup=get_delete_confirmation_keyboard()
    )

@router.message(F.text == ButtonTexts.BACK)
async def back_handler(message: Message, state: FSMContext):
    if not check_user_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED_SHORT)
        return
    
    current_state = await state.get_state()
    await state.clear()
    
    if current_state in [LinkStates.adding_links, LinkStates.deleting_links]:
        await message.answer(Messages.LINKS_MANAGEMENT.format(count=await db.get_urls_count()), reply_markup=get_links_keyboard())
    else:
        await message.answer(Messages.SETTINGS_MENU, reply_markup=get_settings_keyboard())

# Callback handlers
@router.callback_query(F.data == CallbackData.SAVE_LINKS)
async def save_links_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pending_links = data.get('pending_links', [])
    
    saved_count = 0
    for article, url in pending_links:
        if await db.add_url(article, url):
            saved_count += 1
    
    await state.clear()
    await callback.message.edit_text(Messages.LINKS_SAVED.format(count=saved_count))
    await callback.message.answer(Messages.LINKS_MANAGEMENT.format(count=await db.get_urls_count()), reply_markup=get_links_keyboard())
    await callback.answer()

@router.callback_query(F.data == CallbackData.ADD_MORE_LINKS)
async def add_more_links_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(Messages.SEND_MORE_LINKS)
    await callback.answer()

@router.callback_query(F.data == CallbackData.CANCEL_LINKS)
async def cancel_links_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(Messages.OPERATION_CANCELLED)
    await callback.message.answer(Messages.LINKS_MANAGEMENT.format(count=await db.get_urls_count()), reply_markup=get_links_keyboard())
    await callback.answer()

@router.callback_query(F.data == CallbackData.CONFIRM_DELETE)
async def confirm_delete_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    articles_to_delete = data.get('articles_to_delete', [])
    
    deleted_count = await db.delete_by_articles(articles_to_delete)
    
    await state.clear()
    await callback.message.edit_text(Messages.LINKS_DELETED.format(count=deleted_count))
    await callback.message.answer(Messages.LINKS_MANAGEMENT.format(count=await db.get_urls_count()), reply_markup=get_links_keyboard())
    await callback.answer()

@router.callback_query(F.data == CallbackData.CANCEL_DELETE)
async def cancel_delete_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(Messages.DELETE_CANCELLED)
    await callback.message.answer(Messages.LINKS_MANAGEMENT.format(count=await db.get_urls_count()), reply_markup=get_links_keyboard())
    await callback.answer()

# Utility functions
async def parse_reviews_async(parser, url):
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, parse_reviews_sync, parser, url)

def parse_reviews_sync(parser, url):
    article = parser.extract_article_from_url(url)
    if not article:
        return []
    
    root_id = parser.fetch_product_root_id(article)
    if not root_id:
        return []
    
    data = parser.fetch_reviews_data(root_id)
    if not data:
        return []
    
    reviews = data.get('feedbacks', [])
    if not reviews:
        return []
    
    reviews_with_content = parser.filter_reviews_with_content(reviews)
    latest_reviews = parser.get_latest_reviews(reviews_with_content)
    low_rating_reviews = parser.filter_low_rating_reviews(latest_reviews)
    
    return low_rating_reviews

def format_article_reviews_response(article, reviews):
    if not reviews or reviews is None:
        return f"🔍 [{article}] Отзывов с низкой оценкой не найдено"
    
    response = f"🔍 [{article}] Найдено {len(reviews)} отзывов с низкой оценкой:\n\n"
    
    for i, review in enumerate(reviews, 1):
        user_name = review.get('wbUserDetails', {}).get('name', 'Аноним')
        rating = review.get('productValuation', 'Не указано')
        
        text = review.get('text', '').strip()
        pros = review.get('pros', '').strip()
        cons = review.get('cons', '').strip()
        
        content_parts = []
        if text:
            content_parts.append(f"{Emojis.MEMO} {text}")
        if pros:
            content_parts.append(f"{Emojis.PLUS} {pros}")
        if cons:
            content_parts.append(f"{Emojis.MINUS} {cons}")
        
        content = "\n".join(content_parts)
        
        response += f"{i}. {user_name} ({Emojis.STAR} {rating})\n{content}\n\n"
    
    return response