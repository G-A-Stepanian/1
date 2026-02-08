# -*- coding: utf-8 -*-
"""
Главный файл для запуска бота по сбору информации о странах
"""

import time
from config import COUNTRIES, QUESTIONS, SPREADSHEET_ID
from google_sheets import GoogleSheetsManager
from web_search import WebSearcher


def main():
    """Основная функция бота"""

    print("=" * 60)
    print("🤖 БОТ ДЛЯ СБОРА ИНФОРМАЦИИ ПО СТРАНАМ")
    print("=" * 60)

    # Инициализация
    print("\n📊 Подключение к Google Sheets...")
    sheets = GoogleSheetsManager(SPREADSHEET_ID)

    print("🌐 Инициализация поисковика...")
    searcher = WebSearcher()

    # Создаем структуру таблицы
    print("\n🏗️  Создание структуры таблицы...")
    sheets.setup_table_structure(COUNTRIES, QUESTIONS)

    print("\n" + "=" * 60)
    print(f"📍 Стран для анализа: {len(COUNTRIES)}")
    print(f"❓ Вопросов по каждой стране: {len(QUESTIONS)}")
    print(f"📝 Всего ячеек для заполнения: {len(COUNTRIES) * len(QUESTIONS)}")
    print("=" * 60)

    # Спрашиваем подтверждение
    response = input("\n▶️  Начать поиск? (да/нет): ").strip().lower()
    if response not in ['да', 'yes', 'y', 'д']:
        print("❌ Отменено пользователем")
        return

    # Основной цикл: проходим по каждой стране и каждому вопросу
    total_cells = len(COUNTRIES) * len(QUESTIONS)
    current_cell = 0

    for col_idx, country in enumerate(COUNTRIES, start=2):  # Начинаем с B (2-я колонка)
        print("\n" + "🌍" * 30)
        print(f"🌍 СТРАНА: {country.upper()}")
        print("🌍" * 30)

        for row_idx, question in enumerate(QUESTIONS, start=2):  # Начинаем со 2-й строки
            current_cell += 1

            # Проверяем, не заполнена ли ячейка уже
            existing_value = sheets.get_cell_value(row_idx, col_idx)
            if existing_value and existing_value != "":
                print(f"⏭️  [{current_cell}/{total_cells}] Пропускаю (уже заполнено): {question[:50]}...")
                continue

            print(f"\n📌 [{current_cell}/{total_cells}] Вопрос: {question}")

            # Поиск информации
            try:
                answer = searcher.find_info(country, question)

                # Записываем в таблицу
                success = sheets.update_cell(row_idx, col_idx, answer)

                if success:
                    print(f"✅ Записано: {answer[:80]}...")
                else:
                    print(f"❌ Ошибка записи в таблицу")

            except Exception as e:
                print(f"❌ Ошибка при обработке: {e}")
                sheets.update_cell(row_idx, col_idx, f"Ошибка: {str(e)}")

            # Прогресс
            progress = (current_cell / total_cells) * 100
            print(f"📊 Прогресс: {progress:.1f}% ({current_cell}/{total_cells})")

    print("\n" + "=" * 60)
    print("🎉 ГОТОВО! Все данные собраны и записаны в таблицу")
    print("=" * 60)
    print(f"\n📄 Ссылка на таблицу:")
    print(f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")


if __name__ == "__main__":
    main()
