# -*- coding: utf-8 -*-
"""
Модуль для поиска информации через Selenium (улучшенная версия)
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import SEARCH_DELAY


class WebSearcher:
    """Класс для поиска информации через реальный браузер Chrome"""

    def __init__(self, headless=False):
        """
        Инициализация браузера
        headless=True - браузер работает в фоновом режиме (без окна)
        headless=False - браузер открывается визуально (для отладки)
        """
        print("🌐 Запуск браузера Chrome...")

        # Настройки Chrome
        chrome_options = Options()

        if headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--lang=ru')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Автоматическая установка ChromeDriver
        service = Service(ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

        print("✅ Браузер запущен")

    def find_info(self, country, question):
        """
        Поиск информации через Google с помощью Selenium
        """
        # Формируем запрос на русском
        query = f"{country} {question} 2026"

        print(f"🔍 Поиск: {query[:70]}...")

        try:
            # Открываем Google
            self.driver.get('https://www.google.com/search?hl=ru&gl=ru')
            time.sleep(1)

            # Находим поле поиска
            try:
                search_box = self.wait.until(
                    EC.presence_of_element_located((By.NAME, 'q'))
                )
            except:
                search_box = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="q"], input[name="q"]')

            # Вводим запрос
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)

            # Ждём загрузки результатов
            time.sleep(3)

            # НОВЫЙ ПОДХОД: Извлекаем весь видимый текст со страницы результатов
            answer = self._extract_all_visible_text()

            if answer and len(answer) > 30:
                time.sleep(SEARCH_DELAY)
                return self._clean_answer(answer)

            # Если ничего не нашли
            time.sleep(SEARCH_DELAY)
            return "Данные не найдены"

        except Exception as e:
            print(f"⚠️  Ошибка поиска: {e}")
            return f"Ошибка: {str(e)[:100]}"

    def _extract_all_visible_text(self):
        """
        УНИВЕРСАЛЬНЫЙ МЕТОД: Извлекает весь видимый текст из результатов поиска
        """
        try:
            # Пробуем найти основной контейнер с результатами
            main_container = None

            # Варианты селекторов для основного контейнера результатов
            container_selectors = [
                '#search',  # Основной контейнер результатов
                '#rso',  # Results only
                '#center_col',  # Центральная колонка
                'div[id="search"]',
                'div[id="main"]'
            ]

            for selector in container_selectors:
                try:
                    main_container = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if main_container:
                        break
                except:
                    continue

            if not main_container:
                # Если не нашли контейнер, берём body
                main_container = self.driver.find_element(By.TAG_NAME, 'body')

            # Извлекаем текст
            full_text = main_container.text

            if full_text:
                # Разбиваем на строки и берём первые значимые части
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]

                # Фильтруем мусор (навигация, кнопки и т.д.)
                filtered_lines = []
                skip_phrases = [
                    'Все результаты', 'Изображения', 'Карты', 'Видео', 'Новости',
                    'Покупки', 'Ещё', 'Инструменты', 'Настройки', 'История',
                    'Войти', 'Безопасный поиск', 'О результатах'
                ]

                for line in lines[:30]:  # Берём первые 30 строк
                    # Пропускаем короткие строки и навигацию
                    if len(line) < 10:
                        continue

                    # Пропускаем строки с навигацией
                    if any(phrase in line for phrase in skip_phrases):
                        continue

                    filtered_lines.append(line)

                    # Достаточно 5-7 содержательных строк
                    if len(filtered_lines) >= 7:
                        break

                # Объединяем результат
                result = ' | '.join(filtered_lines)

                return result if result else None

        except Exception as e:
            print(f"⚠️  Ошибка извлечения текста: {e}")

        return None

    def _clean_answer(self, text):
        """Очистка и форматирование ответа"""
        if not text:
            return "Данные не найдены"

        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Убираем повторяющиеся фразы (иногда Google дублирует)
        parts = text.split('|')
        unique_parts = []
        seen = set()

        for part in parts:
            part_clean = part.strip().lower()
            if part_clean not in seen and len(part.strip()) > 20:
                unique_parts.append(part.strip())
                seen.add(part_clean)

                # Максимум 3 уникальных части
                if len(unique_parts) >= 3:
                    break

        result = ' | '.join(unique_parts)

        # Ограничиваем длину
        if len(result) > 600:
            result = result[:600] + "..."

        return result if result else "Данные не найдены"

    def close(self):
        """Закрыть браузер"""
        try:
            self.driver.quit()
            print("✅ Браузер закрыт")
        except:
            pass


# Тестирование модуля
if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ ПОИСКОВИКА")
    print("=" * 60)

    searcher = WebSearcher(headless=False)

    # Тестовые запросы
    test_queries = [
        ("Черногория", "стоимость аренды жилья на семью из 4 человек"),
        ("Италия", "цена электроэнергии 1 квт/ч"),
    ]

    for country, question in test_queries:
        print(f"\n{'=' * 60}")
        print(f"Страна: {country}")
        print(f"Вопрос: {question}")
        print(f"{'=' * 60}")

        result = searcher.find_info(country, question)

        print(f"\n✅ РЕЗУЛЬТАТ:")
        print(result)
        print(f"{'=' * 60}\n")

        time.sleep(2)

    searcher.close()
