from enum import Enum

class Commands:
    START = "start"

class ButtonTexts:
    PARSE_REVIEWS = "🔍 Парсить отзывы"
    SETTINGS = "⚙️ Настройки"
    MAIN_MENU = "🏠 Главное меню"
    LINKS = "🔗 Ссылки"
    ADD_LINK = "➕ Добавить ссылку"
    DELETE_LINK = "🗑 Удалить ссылку"
    SHOW_ALL_LINKS = "📋 Показать все ссылки"
    BACK = "⬅️ Назад"

class CallbackData:
    SAVE_LINKS = "save_links"
    ADD_MORE_LINKS = "add_more_links"
    CANCEL_LINKS = "cancel_links"
    CONFIRM_DELETE = "confirm_delete"
    CANCEL_DELETE = "cancel_delete"

class Messages:
    ACCESS_DENIED = "❌ Доступ запрещен. Бот доступен только авторизованным пользователям."
    ACCESS_DENIED_SHORT = "❌ Доступ запрещен."
    
    WELCOME = (
        "Привет! Я бот для парсинга отзывов с Wildberries.\n"
        "Нажми кнопку ниже, чтобы начать парсинг."
    )
    
    SEND_URL = "Отправь ссылку на товар Wildberries:"
    INVALID_URL = "Неверная ссылка. Отправь корректную ссылку на товар Wildberries."
    PARSING_STARTED = "Парсинг начат, подожди..."
    PARSING_ERROR = "Не удалось получить отзывы. Попробуй позже."
    PARSING_EXCEPTION = "Ошибка при парсинге: {error}"
    
    NO_LOW_RATING_REVIEWS = "Отзывов с низкой оценкой не найдено среди последних отзывов."
    FOUND_REVIEWS = "Найдено {count} отзывов с низкой оценкой:\n\n"
    
    # Настройки
    SETTINGS_MENU = "Настройки:"
    MAIN_MENU_TEXT = "Главное меню:"
    
    # Управление ссылками
    LINKS_MANAGEMENT = "Управление ссылками (сохранено: {count}/30):"
    NO_SAVED_LINKS = "Нет сохраненных ссылок."
    NO_SAVED_LINKS_ADD = "Нет сохраненных ссылок. Добавьте ссылки в настройках."
    SAVED_LINKS_LIST = "Сохраненные ссылки:\n\n"
    
    # Добавление ссылок
    SEND_LINKS = "Отправьте ссылки на товары Wildberries (можно несколько за раз):"
    LINKS_LIMIT_REACHED = "Достигнут лимит в 30 ссылок. Удалите старые ссылки."
    NO_VALID_LINKS = "Не найдено корректных ссылок. Попробуйте еще раз."
    LINKS_LIMIT_EXCEEDED = "Превышен лимит! Можно добавить только {available} ссылок."
    CONFIRM_ADD_LINKS = "Добавить эти {count} ссылок для обработки?\n\n"
    LINKS_SAVED = "Сохранено {count} ссылок!"
    OPERATION_CANCELLED = "Операция отменена."
    SEND_MORE_LINKS = "Отправьте еще ссылки:"
    
    # Удаление ссылок
    NO_LINKS_TO_DELETE = "Нет ссылок для удаления."
    DELETE_INSTRUCTIONS = "Введите номера или артикулы для удаления (через запятую):\n\n"
    NO_MATCHING_LINKS = "Не найдено подходящих ссылок для удаления."
    CONFIRM_DELETE_LINKS = "Точно удалить эти артикулы?\n\n"
    LINKS_DELETED = "Удалено {count} ссылок!"
    DELETE_CANCELLED = "Удаление отменено."
    
    # Парсинг
    PARSING_ALL_LINKS = "Начинаю парсинг всех сохраненных ссылок..."
    PARSING_ERROR_ARTICLE = "Ошибка при парсинге {article}: {error}"
    PARSING_COMPLETED = "Парсинг завершен!"

class Emojis:
    SEARCH = "🔍"
    CROSS = "❌"
    MEMO = "📝"
    PLUS = "➕"
    MINUS = "➖"
    STAR = "⭐️"