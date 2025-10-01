import os
from pymongo import MongoClient
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB = os.environ.get("MONGO_DB")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
mongo_logs = mongo_db[MONGO_COLLECTION]

def log_search(search_type, params, results_count):
    """Сохраняет поисковый запрос в MongoDB."""
    doc = {
        "timestamp": datetime.now(timezone.utc), # Беру текущее время UT
        "search_type": search_type,  # Беру тип поиска (например, по ключевому слову или по жанру)
        "params": params, # Беру параметры запроса, которые ввёл пользователь
        "results_count": results_count,  # Беру количество найденных результатов
    }
    try:
        result = mongo_logs.insert_one(doc)  # Сохраняю документ в коллекцию
        print(f"Поисковый запрос сохранен в MongoDB, ID: {result.inserted_id}")
    except Exception as e:
        print("Ошибка сохранения запроса:", e)  # Если не получилось сохранить, вывожу ошибку

def get_logs():
    """Возвращает коллекцию логов для статистики."""
    return mongo_logs # Просто возвращаю коллекцию, с которой потом работаю