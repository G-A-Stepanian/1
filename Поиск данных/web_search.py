# -*- coding: utf-8 -*-
"""
Модуль для поиска информации через Tavily API
"""

import os
import time
from tavily import TavilyClient
from dotenv import load_dotenv
from config import SEARCH_DELAY

# Загружаем переменные окружения
load_dotenv()


class WebSearcher:
    """Класс для поиска информации через Tavily API"""

    def __init__(self):
        """Инициализация Tavily client"""
        api_key = os.getenv('TAVILY_API_KEY')

        if not api_key:
            raise ValueError(
                "❌ Не найден TAVILY_API_KEY в файле .env\n"
                "Получи ключ на: https://app.tavily.com/sign-up\n"
                "Добавь в файл .env: TAVILY_API_KEY=your_key_here"
            )

        self.client = TavilyClient(api_key=api_key)
        print("✅ Tavily API подключен")

    def find_info(self, country, question):
        """
        Поиск информации по конкретному вопросу для страны
        """
        # Формируем запрос на русском
        query = f"{country}: {question} 2026"

        print(f"🔍 Поиск через Tavily: {query[:70]}...")

        try:
            # Выполняем поиск через Tavily
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=3,
                include_answer=True,
                include_raw_content=False
            )

            # Извлекаем ответ
            answer = self._extract_answer(response)

            time.sleep(SEARCH_DELAY)
            return answer

        except Exception as e:
            print(f"⚠️  Ошибка Tavily API: {e}")
            return f"Ошибка API: {str(e)[:100]}"

    def _extract_answer(self, response):
        """Извлечение ответа из результатов Tavily"""

        # Приоритет 1: Готовый ответ от Tavily
        if response.get('answer'):
            answer = response['answer'].strip()
            if len(answer) > 50:
                return self._clean_answer(answer)

        # Приоритет 2: Контент из результатов поиска
        results = response.get('results', [])

        if results:
            combined_text = []

            for result in results[:2]:
                content = result.get('content', '')

                if content:
                    snippet = content[:200].strip()
                    combined_text.append(snippet)

            if combined_text:
                answer = " | ".join(combined_text)
                return self._clean_answer(answer)

        return "Данные не найдены"

    def _clean_answer(self, text):
        """Очистка и форматирование ответа"""
        if not text:
            return "Данные не найдены"

        import re
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        if len(text) > 500:
            text = text[:500] + "..."

        return text

    def close(self):
        """Закрыть соединение"""
        print("✅ Поисковик остановлен")


# Тестирование
if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ TAVILY API")
    print("=" * 60)

    try:
        searcher = WebSearcher()

        result = searcher.find_info("Черногория", "стоимость аренды жилья")

        print(f"\n✅ РЕЗУЛЬТАТ:\n{result}\n")
        print("=" * 60)

        searcher.close()

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
