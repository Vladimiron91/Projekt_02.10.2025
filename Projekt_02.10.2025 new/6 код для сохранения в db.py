# import pymysql
# import os
# import dotenv
# from pathlib import Path
# from pymongo import MongoClient
# from datetime import datetime, timezone
#
# # ========================
# # Конфигурации баз данных
# # ========================
#
# dotenv.load_dotenv(Path('.env'))
# MYSQL_CONFIG = {'host': os.environ.get('host'),
#             'user': os.environ.get('user'),
#             'password': os.environ.get('password'),
#             'database': 'sakila'}
#
# MONGO_URI = (
#     "mongodb://ich_editor:verystrongpassword"
#     "@mongo.itcareerhub.de/?readPreference=primary"
#     "&ssl=false&authMechanism=DEFAULT&authSource=ich_edit"
# )
#
# client = MongoClient(MONGO_URI)
# mongo_db = client["ich_edit"]
# logs_collection = mongo_db["final_project_250425_ptm_vladimir_s"]
#
#
# # ========================
# # Вспомогательные функции
# # ========================
#
# def log_search(search_type, user_input, results_count):
#     """
#     Логирование поискового запроса в MongoDB
#     :param search_type: тип поиска (title/year/genre+year)
#     :param user_input: введённый пользователем запрос
#     :param results_count: количество найденных результатов
#     """
#     doc = {
#         "type": search_type,
#         "input": user_input,
#         "results_count": results_count,
#         "timestamp": datetime.now(timezone.utc)
#     }
#     try:
#         result = logs_collection.insert_one(doc)
#         print(f" Поисковый запрос сохранен в MongoDB, ID: {result.inserted_id}")
#     except Exception as e:
#         print(" Ошибка сохранения запроса:", e)
#
#
# def fetch_and_print(cursor, sql, params, limit):
#     """
#     Выполняет SQL-запрос с пагинацией и выводом результатов
#     :param cursor: курсор MySQL
#     :param sql: SQL-запрос
#     :param params: параметры запроса
#     :param limit: количество записей за раз
#     :return: общее количество найденных записей
#     """
#     offset = 0
#     total = 0
#
#     while True:
#         cursor.execute(sql, params)
#         rows = cursor.fetchall()
#
#         if not rows:
#             if offset == 0:
#                 print("Ничего не найдено")
#             break
#
#         for row in rows:
#             print(f"{row[0]} | {row[1]} ({row[2]})")
#             print(f"Описание: {row[3]}\n")
#             total += 1
#
#         if len(rows) < limit:
#             break
#
#         ans = input("Показать ещё? (y/n): ")
#         if ans.lower() != "y":
#             break
#         offset += limit
#         # обновляем параметры с новым offset
#         params = tuple(list(params[:-1]) + [offset])
#
#     return total
#
#
# def get_years_range(years_input):
#     """
#     Преобразует ввод пользователя в диапазон или год
#     :param years_input: строка с годом или диапазоном
#     :return: tuple (start_year, end_year) или int (year)
#     """
#     if "-" in years_input:
#         try:
#             start, end = map(int, years_input.split("-"))
#             return start, end
#         except ValueError:
#             print("Ошибка ввода диапазона")
#             return None
#     else:
#         try:
#             year = int(years_input)
#             return year
#         except ValueError:
#             print("Ошибка ввода года")
#             return None
#
#
# # ========================
# # Основные функции поиска
# # ========================
#
# def search_by_title(cursor):
#     """Поиск фильмов по названию"""
#     keyword = input("Введите слово в названии: ")
#     limit = 2
#     sql = """
#         SELECT film_id, title, release_year, description
#         FROM film
#         WHERE title LIKE %s
#         LIMIT %s OFFSET %s
#     """
#     total = fetch_and_print(cursor, sql, (f"%{keyword}%", limit, 0), limit)
#     log_search("title", keyword, total)
#
#
# def search_by_year(cursor):
#     """Поиск фильмов по году или диапазону"""
#     years_input = input("Введите год или диапазон (например: 2005 или 2005-2010): ")
#     limit = 2
#     years = get_years_range(years_input)
#     if years is None:
#         return
#
#     if isinstance(years, tuple):
#         sql = """
#             SELECT film_id, title, release_year, description
#             FROM film
#             WHERE release_year BETWEEN %s AND %s
#             ORDER BY release_year
#             LIMIT %s OFFSET %s
#         """
#         params = (years[0], years[1], limit, 0)
#     else:
#         sql = """
#             SELECT film_id, title, release_year, description
#             FROM film
#             WHERE release_year = %s
#             ORDER BY title
#             LIMIT %s OFFSET %s
#         """
#         params = (years, limit, 0)
#
#     total = fetch_and_print(cursor, sql, params, limit)
#     log_search("year", years_input, total)
#
#
# def search_by_genre_and_year(cursor):
#     """Поиск фильмов по жанру и году/диапазону"""
#     cursor.execute("SELECT category_id, name FROM category ORDER BY name")
#     categories = cursor.fetchall()
#     print("\nЖанры:")
#     for c in categories:
#         print(f"{c[0]}. {c[1]}")
#
#     try:
#         cat_id = int(input("\nВведите ID жанра: "))
#     except ValueError:
#         print("Ошибка ввода жанра")
#         return
#
#     years_input = input("Введите год или диапазон (например: 2005 или 2005-2010): ")
#     limit = 2
#     years = get_years_range(years_input)
#     if years is None:
#         return
#
#     if isinstance(years, tuple):
#         sql = """
#             SELECT f.film_id, f.title, f.release_year, f.description
#             FROM film f
#             JOIN film_category fc ON f.film_id = fc.film_id
#             WHERE fc.category_id = %s
#               AND f.release_year BETWEEN %s AND %s
#             ORDER BY f.release_year
#             LIMIT %s OFFSET %s
#         """
#         params = (cat_id, years[0], years[1], limit, 0)
#     else:
#         sql = """
#             SELECT f.film_id, f.title, f.release_year, f.description
#             FROM film f
#             JOIN film_category fc ON f.film_id = fc.film_id
#             WHERE fc.category_id = %s
#               AND f.release_year = %s
#             ORDER BY f.title
#             LIMIT %s OFFSET %s
#         """
#         params = (cat_id, years, limit, 0)
#
#     total = fetch_and_print(cursor, sql, params, limit)
#     log_search("genre+year", f"genre_id={cat_id}, years={years_input}", total)
#
#
# # ========================
# # Главный блок
# # ========================
#
# def main():
#     """Главная функция программы"""
#     conn = pymysql.connect(**MYSQL_CONFIG)
#     try:
#         with conn.cursor() as cursor:
#             mode = input(
#                 "Выберите режим: 1 - По названию, 2 - По году, 3 - По жанру и году: "
#             )
#             if mode == "1":
#                 search_by_title(cursor)
#             elif mode == "2":
#                 search_by_year(cursor)
#             elif mode == "3":
#                 search_by_genre_and_year(cursor)
#             else:
#                 print("Неверный выбор")
#     finally:
#         conn.close()
