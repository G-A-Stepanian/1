# -*- coding: utf-8 -*-
"""
Модуль для поиска информации в интернете
"""

import requests
import time
import re
from bs4 import BeautifulSoup
from config import SEARCH_DELAY, MAX_RETRIES, TIMEOUT


class WebSearcher:
    """Класс для поиска информации через различные источники"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def search_google(self, query):
        """
        Поиск через Google (используя requests)
        Возвращает список результатов поиска
        """
        try:
            url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            response = self.session.get(url, timeout=TIMEOUT)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []

                # Ищем блоки с результатами
                for g in soup.find_all('div', class_='g')[:5]:  # Первые 5 результатов
                    title_elem = g.find('h3')
                    link_elem = g.find('a')
                    snippet_elem = g.find('div', class_=['VwiC3b', 'yXK7lf'])

                    if title_elem and link_elem:
                        results.append({
                            'title': title_elem.get_text(),
                            'url': link_elem.get('href'),
                            'snippet': snippet_elem.get_text() if snippet_elem else ''
                        })

                return results

        except Exception as e:
            print(f"⚠️  Ошибка поиска в Google: {e}")

        return []

    def search_duckduckgo(self, query):
        """
        Альтернативный поиск через DuckDuckGo
        """
        try:
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            response = self.session.get(url, timeout=TIMEOUT)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []

                for result in soup.find_all('div', class_='result')[:5]:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')

                    if title_elem:
                        results.append({
                            'title': title_elem.get_text(),
                            'url': title_elem.get('href'),
                            'snippet': snippet_elem.get_text() if snippet_elem else ''
                        })

                return results

        except Exception as e:
            print(f"⚠️  Ошибка поиска в DuckDuckGo: {e}")

        return []

    def find_info(self, country, question):
        """
        Поиск информации по конкретному вопросу для страны
        """
        # Формируем поисковый запрос
        query = f"{country} {question} 2026"

        print(f"🔍 Ищу: {query}")

        # Пробуем поиск через Google
        results = self.search_google(query)

        # Если Google не дал результатов, пробуем DuckDuckGo
        if not results:
            time.sleep(SEARCH_DELAY)
            results = self.search_duckduckgo(query)

        # Обрабатываем результаты
        if results:
            # Извлекаем наиболее релевантную информацию
            answer = self._extract_answer(results, question)
            time.sleep(SEARCH_DELAY)  # Задержка между запросами
            return answer

        return "Данные не найдены"

    def _extract_answer(self, results, question):
        """
        Извлечение ответа из результатов поиска
        Простая эвристика - берем первый snippet с ссылкой
        """
        if results and results[0].get('snippet'):
            snippet = results[0]['snippet']
            url = results[0].get('url', '')

            # Очищаем snippet от лишних символов
            snippet = snippet.strip()

            # Ограничиваем длину ответа
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."

            # Возвращаем snippet + источник
            return f"{snippet}\n[Источник: {url}]"

        return "Данные не найдены"


# Тестирование модуля
if __name__ == "__main__":
    searcher = WebSearcher()
    result = searcher.find_info("Черногория", "стоимость аренды жилья на семью из 4 человек")
    print(f"\n✅ Результат:\n{result}")
