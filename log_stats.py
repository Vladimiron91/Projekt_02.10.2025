from collections import Counter
from log_writer import get_logs

def most_frequent_searches(n=5):
    """Возвращает n самых частых поисковых запросов по параметрам."""
    mongo_logs = get_logs()
    all_searches = list(mongo_logs.find({}, {"params": 1}))
    counter = Counter(
        [str(s["params"]) for s in all_searches if s.get("params")]
    )
    return counter.most_common(n)

def last_searches(n=5):
    """Возвращает n последних поисковых запросов."""
    mongo_logs = get_logs()
    return list(mongo_logs.find().sort("timestamp", -1).limit(n))