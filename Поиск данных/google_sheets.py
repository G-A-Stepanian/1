# -*- coding: utf-8 -*-
"""
Модуль для работы с Google Sheets API (Service Account version)
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Области доступа для Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsManager:
    """Класс для управления Google Sheets"""

    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.service = self._authenticate()

    def _authenticate(self):
        """Аутентификация через Service Account"""
        creds = service_account.Credentials.from_service_account_file(
            'service_account.json',
            scopes=SCOPES
        )

        return build('sheets', 'v4', credentials=creds)

    def setup_table_structure(self, countries, questions):
        """
        Настройка структуры таблицы: столбцы = страны, строки = вопросы
        """
        try:
            # Формируем заголовки (первая строка - страны)
            headers = ['Вопрос'] + countries

            # Формируем данные (первая колонка - вопросы)
            data = [headers]
            for question in questions:
                row = [question] + [''] * len(countries)
                data.append(row)

            # Записываем в таблицу
            body = {'values': data}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range='A1',
                valueInputOption='RAW',
                body=body
            ).execute()

            print(f"✅ Структура таблицы создана: {result.get('updatedCells')} ячеек обновлено")

            # Форматируем первую строку и первый столбец (жирный текст)
            self._format_headers()

            return True

        except HttpError as error:
            print(f"❌ Ошибка при создании структуры: {error}")
            return False

    def _format_headers(self):
        """Форматирование заголовков (жирный текст)"""
        try:
            requests = [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": 0,
                            "endRowIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {"bold": True}
                            }
                        },
                        "fields": "userEnteredFormat.textFormat.bold"
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": 0,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {"bold": True}
                            }
                        },
                        "fields": "userEnteredFormat.textFormat.bold"
                    }
                }
            ]

            body = {'requests': requests}
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()

        except HttpError as error:
            print(f"⚠️  Не удалось отформатировать заголовки: {error}")

    def update_cell(self, row, col, value):
        """
        Обновление конкретной ячейки
        row: номер строки (начиная с 1)
        col: номер столбца (начиная с 1)
        value: значение для записи
        """
        try:
            # Преобразуем номер столбца в букву (1->A, 2->B, и т.д.)
            col_letter = self._number_to_column_letter(col)
            cell_range = f'{col_letter}{row}'

            body = {'values': [[value]]}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=cell_range,
                valueInputOption='RAW',
                body=body
            ).execute()

            return True

        except HttpError as error:
            print(f"❌ Ошибка при обновлении ячейки {cell_range}: {error}")
            return False

    def _number_to_column_letter(self, n):
        """Преобразование номера столбца в букву (1->A, 27->AA)"""
        result = ""
        while n > 0:
            n -= 1
            result = chr(n % 26 + ord('A')) + result
            n //= 26
        return result

    def get_cell_value(self, row, col):
        """Получение значения из ячейки"""
        try:
            col_letter = self._number_to_column_letter(col)
            cell_range = f'{col_letter}{row}'

            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=cell_range
            ).execute()

            values = result.get('values', [])
            if values and values[0]:
                return values[0][0]
            return ''

        except HttpError as error:
            print(f"❌ Ошибка при чтении ячейки: {error}")
            return ''
