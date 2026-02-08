# -*- coding: utf-8 -*-
"""
Главный файл для запуска бота по сбору информации о странах
Использует Tavily API для поиска данных
"""

import time
from config import COUNTRIES, QUESTIONS, SPREADSHEET_ID
from google_sheets import GoogleSheetsManager
from web_search import WebSearcher


def main():
    """Основная функция бота"""

    print("=" * 70)
    print("🤖 БОТ ДЛЯ СБОРА ИНФОРМАЦИИ ПО СТРАНАМ (TAVILY API)")
    print("=" * 70)

    # Инициализация Google Sheets
    print("\n📊 Подключение к Google Sheets...")
    try:
        sheets = GoogleSheetsManager(SPREADSHEET_ID)
        print("✅ Google Sheets подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения к Google Sheets: {e}")
        print("Проверь наличие файла service_account.json и доступ к таблице")
        return

    # Инициализация Tavily поисковика
    print("\n🌐 Подключение к Tavily API...")
    try:
        searcher = WebSearcher()
    except Exception as e:
        print(f"❌ Ошибка подключения к Tavily API: {e}")
        print("Проверь наличие TAVILY_API_KEY в файле .env")
        return

    # Создаем структуру таблицы
    print("\n🏗️  Создание структуры таблицы...")
    sheets.setup_table_structure(COUNTRIES, QUESTIONS)

    print("\n" + "=" * 70)
    print(f"📍 Стран для анализа: {len(COUNTRIES)}")
    print(f"❓ Вопросов по каждой стране: {len(QUESTIONS)}")
    print(f"📝 Всего ячеек для заполнения: {len(COUNTRIES) * len(QUESTIONS)}")
    print(f"⏱️  Примерное время работы: {(len(COUNTRIES) * len(QUESTIONS) * 3) // 60} минут")
    print("=" * 70)

    # Спрашиваем подтверждение
    response = input("\n▶️  Начать поиск? (да/нет): ").strip().lower()
    if response not in ['да', 'yes', 'y', 'д']:
        print("❌ Отменено пользователем")
        searcher.close()
        return

    # Основной цикл: проходим по каждой стране и каждому вопросу
    total_cells = len(COUNTRIES) * len(QUESTIONS)
    current_cell = 0
    success_count = 0
    skip_count = 0
    errors_count = 0

    start_time = time.time()

    try:
        for col_idx, country in enumerate(COUNTRIES, start=2):  # Начинаем с B (2-я колонка)
            print("\n" + "🌍" * 35)
            print(f"🌍 СТРАНА: {country.upper()}")
            print("🌍" * 35)

            for row_idx, question in enumerate(QUESTIONS, start=2):  # Начинаем со 2-й строки
                current_cell += 1

                # Проверяем, не заполнена ли ячейка уже
                existing_value = sheets.get_cell_value(row_idx, col_idx)
                if existing_value and existing_value.strip() and existing_value != "":
                    print(f"⏭️  [{current_cell}/{total_cells}] Пропускаю (заполнено): {question[:50]}...")
                    skip_count += 1
                    continue

                print(f"\n📌 [{current_cell}/{total_cells}] {question[:70]}...")

                # Поиск информации
                try:
                    answer = searcher.find_info(country, question)

                    # Записываем в таблицу
                    success = sheets.update_cell(row_idx, col_idx, answer)

                    if success:
                        if "Данные не найдены" in answer or "Ошибка" in answer:
                            print(f"⚠️  Записано: {answer[:80]}...")
                            errors_count += 1
                        else:
                            print(f"✅ Записано: {answer[:80]}...")
                            success_count += 1
                    else:
                        print(f"❌ Ошибка записи в таблицу")
                        errors_count += 1

                except Exception as e:
                    print(f"❌ Ошибка при обработке: {e}")
                    error_msg = f"Ошибка: {str(e)[:100]}"
                    sheets.update_cell(row_idx, col_idx, error_msg)
                    errors_count += 1

                # Прогресс
                progress = (current_cell / total_cells) * 100
                elapsed = time.time() - start_time
                avg_time = elapsed / current_cell if current_cell > 0 else 0
                remaining = (total_cells - current_cell) * avg_time

                print(
                    f"📊 Прогресс: {progress:.1f}% | Успешно: {success_count} | Пропущено: {skip_count} | Ошибок: {errors_count}")
                print(
                    f"⏱️  Прошло: {int(elapsed // 60)}м {int(elapsed % 60)}с | Осталось: ~{int(remaining // 60)}м {int(remaining % 60)}с")

    finally:
        # Закрываем соединение
        searcher.close()

    # Итоговая статистика
    total_time = time.time() - start_time

    print("\n" + "=" * 70)
    print("🎉 РАБОТА ЗАВЕРШЕНА!")
    print("=" * 70)
    print(f"✅ Успешно обработано: {success_count}/{total_cells}")
    print(f"⏭️  Пропущено (уже было): {skip_count}")
    print(f"❌ Ошибок/не найдено: {errors_count}")
    print(f"⏱️  Общее время работы: {int(total_time // 60)}м {int(total_time % 60)}с")
    print("=" * 70)
    print(f"\n📄 Открой таблицу:")
    print(f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
    print("\n💡 Совет: Проверь ячейки с 'Данные не найдены' - возможно, нужно уточнить запрос")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем (Ctrl+C)")
        print("💾 Данные, которые успели записаться, сохранены в таблице")
    except Exception as e:
        print(f"\n\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
