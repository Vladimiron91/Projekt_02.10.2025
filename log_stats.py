from collections import Counter  # Беру Counter, чтобы посчитать, сколько раз встречается каждый запрос
from log_writer import get_logs  # Импортирую функцию get_logs для подключения к MongoDB

def most_frequent_searches(n=5):
    """Возвращает n самых частых поисковых запросов по параметрам."""
    mongo_logs = get_logs()
    # Достаю все документы, выбираю только поле "params"
    all_searches = list(mongo_logs.find({}, {"params": 1}))
    # преобразую их в строку и подсчитываю частоту каждого запроса
    counter = Counter(
        [str(s["params"]) for s in all_searches if s.get("params")]
    )
    return counter.most_common(n) # Возвращаю n самых частых запросов

def last_searches(n=5):
    """Возвращает n последних поисковых запросов."""
    mongo_logs = get_logs()
    # Беру все документы, сортирую по времени по убыванию и ограничиваю n последних
    return list(mongo_logs.find().sort("timestamp", -1).limit(n))