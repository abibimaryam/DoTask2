import re
import sqlite3
from notion_client import Client
from aiogram.types import Message,Update
from aiogram import types,Bot
from tgbot.data.config import BOT_TOKEN

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup



saved_token = None
db_id = None

def get_all(text: str):
    pattern = r'(https?://[^\s]+)\s+(.+?)\s+(\w+)\s+(\d+)'
    matches = re.findall(pattern, text)
    
    # Преобразуем список совпадений в нужный формат
    return [(url, title, category, int(priority)) for url, title, category, priority in matches]

from urllib.parse import urlparse

def get_source_from_url(url: str) -> str:

    # Парсим доменное имя из URL
    try:
        domain = urlparse(url).netloc.lower()
        
        # Список соответствий доменов
        sources = {
            "youtube.com": "YouTube",
            "youtu.be": "YouTube",
            "twitter.com": "Twitter",
            "instagram.com": "Instagram",
            "tiktok.com": "TikTok",
            "facebook.com": "Facebook",
            "linkedin.com": "LinkedIn",
            "reddit.com": "Reddit",
            "t.me": "Telegram",
            "vk.com": "ВКонтакте",
            "ok.ru": "Одноклассники"
        }
        
        # Определение источника по домену
        for key, source in sources.items():
            if key in domain:
                return source
        
        # Если не найдено
        return "Неизвестный источник"
    except Exception as e:
        print(f"Ошибка при определении источника: {e}")
        return "Ошибка анализа"


# Сохранение ссылки в базу данных SQLite
def save_link_to_db(url: str, title: str, category: str, priority: int,source:str):
    conn = sqlite3.connect('links.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO links (url, title, category, priority,source)
    VALUES (?, ?, ?, ?,?)''', (url, title, category, priority,source))
    
    conn.commit()
    conn.close()

class Form(StatesGroup):
    token = State()  # State for Notion token
    db_id = State()  # State for the database ID
    links = State()

async def save_to_db_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите Notion токен\nНапример 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"
    )
    await state.set_state(Form.token)

async def process_token(message: types.Message, state: FSMContext):
    global saved_token
    
    token = message.text
    await state.update_data(token=token)
    saved_token = token
    
    await message.answer("Теперь введите ID вашей базы данных.Например 1463316ae38880cfa30cee80a4721443")
    await state.set_state(Form.db_id)

async def process_db_id(message: types.Message, state: FSMContext):
    global db_id 
    
    db_id = message.text
    await state.update_data(db_id=db_id)
    
    print(f"Database ID received: {db_id}")

    await message.answer(
        """Введите ссылку для сохранения в формате:
        Url Заголовок Категория Приоритет.
        
        Например:
        https://www.youtube.com Ютуб Категория 1.
        
        Можете отправлять по несколько ссылок:
        Например:
        https://www.google.com/ Заголовок Категория 2
        https://www.youtube.com Заголовок Категория 1

        Главное придерживайтесь формата."""
    )
    
    # await state.set_state(Form.next())
    await state.set_state(Form.links)
    await message.answer("Теперь отправьте ссылки.")





def save_link_to_notion(url: str, title: str, category: str, priority: int, source: str):
    # ID базы данных в Notion
    notion = Client(auth=saved_token)
    database_id = db_id
    print(database_id)

    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "url": {"multi_select": [{"name": url}]},  # Передаем URL как список меток
            "title": {"rich_text": [{"text": {"content": title}}]},  # Заголовок в rich_text
            "category": {"rich_text": [{"text": {"content": category}}]},  # Категория в rich_text
            "priority": {"number": priority},  # Приоритет как число
            "source": {"rich_text": [{"text": {"content": source}}]}  # Источник в rich_text
        }
    )
    print("Ссылка сохранена в Notion")



def clear_all_links_from_db():
    conn = sqlite3.connect('links.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM links")
    conn.commit()
    conn.close()

def clear_notion_database(database_id: str):
    notion = Client(auth=saved_token)
    try:
        results = notion.databases.query(database_id=database_id)
        
        for page in results['results']:
            page_id = page['id']
            notion.pages.update(page_id, archived=True)
            print(f"Страница с ID {page_id} архивирована.")
        
        print("Все страницы из базы данных архивированы.")
    except Exception as e:
        print(f"Произошла ошибка при очистке базы данных: {e}")
        
bot = Bot(token=BOT_TOKEN)
async def log_to_channel(text: str):
    chat_id = "@Task2DoChanel" 
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в канал: {e}")
    
async def handle_message(message: types.Message):
    text = message.text
    links = get_all(text)
    
    if links:
        for url, title, category, priority in links:
            source=get_source_from_url(url)
            # Сохраняем каждую ссылку в базу данных SQLite и Notion
            save_link_to_db(url, title, category, priority,source)
            save_link_to_notion(url, title, category, priority,source)

            log_message = (f"Новая ссылка сохранена:\n"
                           f"URL: {url}\n"
                           f"Заголовок: {title}\n"
                           f"Категория: {category}\n"
                           f"Приоритет: {priority}\n"
                           f"Источник: {source}")
            await log_to_channel(log_message)
        
        await message.reply(f"Сохранено {len(links)} ссылок.")
    else:
        await message.reply("Не похоже на ссылку")
    




async def clear_db_handler(message:types.Message):
    clear_all_links_from_db()
    clear_notion_database(db_id)
    await message.reply(f"Базы данных очищены")