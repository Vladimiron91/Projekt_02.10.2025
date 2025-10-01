
############## Точка входа и мену.
import pymysql
from mysql_connector import search_by_title, search_by_year, search_by_genre_and_years, MYSQL_CONFIG
from log_stats import most_frequent_searches, last_searches

if __name__ == "__main__":
    print("Добро пожаловать в виртуальный кинотеатр!")
    print("Здесь вы можете искать фильмы по названии, году выпуска или жанру.\n")

    connection = pymysql.connect(**MYSQL_CONFIG)
    try:
        with connection.cursor() as cursor:
            while True:
                print("\nМеню:")
                print("1 - Поиск по названию")
                print("2 - Поиск по году")
                print("3 - Поиск по жанру и году")
                print("4 - Показать 5 самых частых запросов")
                print("5 - Показать 5 последних запросов")
                print("0 - Выход")

                choice = input("Выберите опцию: ")

                if choice == "1":
                    search_by_title(cursor)
                elif choice == "2":
                    search_by_year(cursor)
                elif choice == "3":
                    search_by_genre_and_years(cursor)
                elif choice == "4":
                    top_searches = most_frequent_searches()
                    print("\n Частые поисковые запросы:")
                    for params, count in top_searches:
                        print(f"{params} — {count} раз(а)")
                elif choice == "5":
                    recent = last_searches()
                    print("\n Последний поисковые запросы:")
                    for doc in recent:
                        ts = doc["timestamp"].strftime("%Y-%m-%d %H:%M")
                        print(
                            f"{ts} | {doc['search_type']} | {doc['params']} "
                            f"({doc['results_count']} результатов)"
                        )
                elif choice == "0":
                    print("Выход из программы.")
                    break
                else:
                    print("Неверный выбор. Попробуйте снова.")
    finally:
        connection.close()