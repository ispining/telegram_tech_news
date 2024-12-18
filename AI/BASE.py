import os
import time

import requests
import json
import argparse
from AI import prompts
import undetected_chromedriver as uc

arg_parser = argparse.ArgumentParser(description="GeminiInterpreter")
arg_parser.add_argument("--jailbreak", action="store_true", help="Jailbreak mode")
arg_parser.add_argument("--temperature", type=float, default=1.0, help="Temperature")
arg_parser.add_argument("--top_k", type=float, default=40.0, help="Model top_k")
arg_parser.add_argument("--top_p", type=float, default=0.95, help="Model top_p")
arg_parser.add_argument("--max_output_tokens", type=int, default=8192, help="Max output tokens")
arg_parser.add_argument("--repetition_penalty", type=float, default=1.0, help="Repetition penalty")

args = arg_parser.parse_args()
settings = json.load(open("AI/settings.json", "r", encoding="utf-8"))


class Gen:
    """
Основной класс для работы с моделью генерации текста Gemini от Google.
Перед использованием - переназначьте переменную Gen.API_KEY на свой ключ от GeminiAI.

    Attributes:
        history: Список словарей с историею диалога.
        system_instructions: Список словарей с инструкциями системы.
    Methods:
        history_add(role, content): Добавляет сообщение в историю диалога.
        generate(): Генерирует текст на основе истории диалога.
        export_history(filename): Сохраняет историю диалога в файл.
        import_history(filename): Загружает историю диалога из файла.
        clear_history(filename): Очищает историю диалога.
    """
    def __init__(self, history=[], system_instructions=None):
        """Инициализация класса.

        Args:
            history (list, optional): Список словарей с историей диалога. Defaults to [].
            system_instructions (list, optional): Список словарей с инструкциями системы. Defaults to None.
"""
        self.API_KEY = open("AI/gemini_api_key", "r", encoding="utf-8").read()
        self.history = history
        self.system_instructions = system_instructions

    def history_add(self, role, content):
        """
        Добавляет сообщение в историю диалога.

        Args:
            role (str): Роль отправителя сообщения.
            content (str): Текст сообщения.

        Returns:
            None
        """
        self.history.append({"role": role, "parts": [{"text": content}]})

    def generate(self):
        settings = json.load(open("AI/settings.json", "r", encoding="utf-8"))

        """
Генерирует текст на основе истории диалога из переменной Gen.history.

        Returns:
            str: Генерированный текст.
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.API_KEY}"

        data = {"contents": self.history}

        if self.system_instructions:
            data["systemInstruction"] = {"role": "user", "parts": self.system_instructions}

        data["generationConfig"] = {
            "temperature": settings["temperature"]
        }

        data["safetySettings"] = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_CIVIC_INTEGRITY", "threshold": "BLOCK_NONE"}
        ]

        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            print(response.json())
        try:
            result = str(response.json()["candidates"][0]["content"]["parts"][0]["text"])
        except KeyError:
            error = response.json()["error"]
            if error['code'] == 503:
                time.sleep(10)
                result = self.generate()
            elif error['code'] == 400:
                print(error['message'])
                result = "pass"
            else:
                print(error)
                result = "pass"

        return result

    def export_history(self, filename):
        """
        Сохраняет историю диалога в файл.

        Args:
            filename (str): Имя файла.

        Returns:
            None
        """
        import pickle

        with open(filename, "wb") as f:
            pickle.dump(self.history, f)

    def import_history(self, filename):
        """
        Загружает историю диалога из файла.

        Args:
            filename (str): Имя файла.

        Returns:
            None
        """
        import pickle

        with open(filename, "rb") as f:
            self.history = pickle.load(f)

    def import_history_anyway(self, filename):
        try:
            self.import_history(filename)
        except FileNotFoundError:
            self.export_history(filename)  # Сохранит пустой список, так как беседа не начата
            self.import_history_anyway(filename)

    def clear_history(self, filename):
        """
        Очищает историю диалога.

        Args:
            filename (str): Имя файла.

        Returns:
            None
        """
        os.remove(filename)
        self.history = []


