import os
from dotenv import load_dotenv
from log_writer import log_search
from formatter import format_film

load_dotenv() # Загружаю переменные окружения из .env


MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST"),
    "user": os.environ.get("MYSQL_USER"),
    "password": os.environ.get("MYSQL_PASSWORD"),
    "database": os.environ.get("MYSQL_DATABASE"),
}


def search_by_title(cursor):
    """Поиск фильмов по названию."""
    keyword = input("Введите слово в названии: ")
    offset = 0
    limit = 10  # Показываю по 10 результатов за раз
    total_results = 0

    while True: # Цикл для постраничного вывода
        sql = """
            SELECT film_id, title, release_year, description
            FROM film
            WHERE title LIKE %s
            LIMIT %s OFFSET %s
        """
        cursor.execute(sql, (f"%{keyword}%", limit, offset))
        rows = cursor.fetchall()

        if not rows:
            if offset == 0:
                print("Ничего не найдено")
            break

        for film in rows: # Показываю все найденные фильмы
            print(format_film(film))
            total_results += 1 #Счётчик

        if len(rows) < limit: # Если меньше 10 результатов, значит конец
            break

        show_more = input("Показать ещё? (y/n): ")
        if show_more.lower() != "y":
            break
        offset += limit

    log_search("Название: ", {"По популярности: ": keyword}, total_results)


def search_by_year(cursor):
    """Поиск фильмов по году или диапазону лет."""
    years_input = input("Введите год или диапазон (например: 2005 или 1990-2025): ")
    offset = 0
    limit = 10
    total_results = 0

    if "-" in years_input:
        try:
            start_year, end_year = map(int, years_input.split("-"))
            sql = """
                SELECT film_id, title, release_year, description
                FROM film
                WHERE release_year BETWEEN %s AND %s
                ORDER BY release_year
                LIMIT %s OFFSET %s
            """
            params = (start_year, end_year, limit, offset)
            log_params = {"start_year": start_year, "end_year": end_year}
        except ValueError:
            print("Ошибка ввода диапазона")
            return
    else:
        try:
            year = int(years_input)
            sql = """
                SELECT film_id, title, release_year, description
                FROM film
                WHERE release_year = %s
                ORDER BY title
                LIMIT %s OFFSET %s
            """
            params = (year, limit, offset)
            log_params = {"year": year}
        except ValueError:
            print("Ошибка ввода года")
            return

    while True:
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        if not rows:
            if offset == 0:
                print("Ничего не найдено")
            break

        for film in rows:
            print(format_film(film))
            total_results += 1

        if len(rows) < limit:
            break

        show_more = input("Показать ещё? (y/n): ")
        if show_more.lower() != "y":
            break
        offset += limit
        if "-" in years_input:
            params = (start_year, end_year, limit, offset)
        else:
            params = (year, limit, offset)

    # Сохраняю запрос в MongoDB
    log_search("Год: ", log_params, total_results)


def search_by_genre_and_years(cursor):
    """Поиск фильмов по жанру и году."""
    cursor.execute("SELECT category_id, name FROM category ORDER BY name")
    categories = cursor.fetchall()

    print("\nЖанры:")
    for cat in categories:
        print(f"{cat[0]}. {cat[1]}")

    try:
        category_id = int(input("\nВведите ID жанра: "))
    except ValueError:
        print("Ошибка ввода жанра")
        return

    years_input = input("Введите год или диапазон (например: 2005 или 1990-2025): ")
    offset = 0
    limit = 10
    total_results = 0

    if "-" in years_input:
        try:
            start_year, end_year = map(int, years_input.split("-"))
            sql = """
                SELECT f.film_id, f.title, f.release_year, f.description
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                WHERE fc.category_id = %s
                  AND f.release_year BETWEEN %s AND %s
                ORDER BY f.release_year
                LIMIT %s OFFSET %s
            """
            params = (category_id, start_year, end_year, limit, offset)
            log_params = {"genre_id": category_id, "start_year": start_year, "end_year": end_year}
        except ValueError:
            print("Ошибка диапазона")
            return
    else:
        try:
            year = int(years_input)
            sql = """
                SELECT f.film_id, f.title, f.release_year, f.description
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                WHERE fc.category_id = %s
                  AND f.release_year = %s
                ORDER BY f.title
                LIMIT %s OFFSET %s
            """
            params = (category_id, year, limit, offset)
            log_params = {"genre_id": category_id, "year": year}
        except ValueError:
            print("Ошибка года")
            return

    while True:
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        if not rows:
            if offset == 0:
                print("Ничего не найдено")
            break

        for film in rows:
            print(format_film(film))
            total_results += 1

        if len(rows) < limit:
            break

        show_more = input("Показать ещё? (y/n): ")
        if show_more.lower() != "y":
            break
        offset += limit
        if "-" in years_input:
            params = (category_id, start_year, end_year, limit, offset)
        else:
            params = (category_id, year, limit, offset)

    log_search("genre+year", log_params, total_results)