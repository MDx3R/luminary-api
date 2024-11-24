from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse
from rest_framework.request import HttpRequest

import dataclasses

from typing import Dict, List, Iterator, overload

from .base import once, Singleton
from .managers import LocalFileManager, RemoteFileManager
from .connection import GPTConnection

# Create your services here.

class Service(Singleton):
    """
    Базовый класс сервисов
    """
    pass

class FileService(Service):
    """
    Отвечает за обработку файлов
    """

    fileManager = None

    @once
    def __init__(self):
        self.fileManager = None
        pass

    def listFiles(self, path: str) -> List[str]:
        pass
    
    def readFile(self, path: str, name: str) -> str:
        pass

    @overload
    def saveFile(self, path: str, filename: str, file: str, returning=False) -> None | str:
        pass

    @overload
    def saveFile(self, path: str, file: UploadedFile, returning=False) -> None | Iterator[bytes]:
        pass

    def removeFile(self, path: str, name: str) -> None:
        pass
    
    def clearDir(self, path: str) -> None:
        pass

class GPTService(Service):
    """
    Отвечает за общение с GPT-моделью
    """

    @dataclasses
    class Chat():
        messages: List[Dict[str, str]] = None
        tokens: int = 0
        commited: bool = False

        def clear(self):
            pass

    connection = None

    @once
    def __init__(self):
        self.connection = GPTConnection()

    def getConversation(self, id: str) -> Chat:
        pass

    def createConversation(self, id: str, context: List[Dict[str, str]]) -> None:
        pass

    def closeConversation(self, id: str) -> None:
        pass

    def sendMessage(self, id: str, prompt: str) -> str:
        pass

    def clearContext(self, id: str) -> None:
        pass

class EnvironmentService(Service):
    """
    Отвечает за бизнес-логику обработки запросов к окружению.
    """

    fileService = None
    gptService = None

    @once
    def __init__(self):
        self.fileService = FileService()
        self.gptService = GPTService()

    def clearEnvironment(self, id: str) -> JsonResponse:
        """Очищает файлы окружения и контекст модели"""
        pass
    
    @overload
    def saveFile(self, id: str, file: UploadedFile) -> JsonResponse:
        """Загружает файл, представленный `UploadedFile`, в хранилище"""
        pass

    @overload
    def saveFile(self, id: str, file: str) -> JsonResponse:
        """Загружает файл, представленный `str`, в хранилище"""
        pass

    @overload
    def updateFile(self, id: str, file: UploadedFile) -> JsonResponse:
        """Дополняет файл в хранилище файлом с тем же именем, представленным `UploadedFile`"""
        pass

    @overload
    def updateFile(self, id: str, file: str) -> JsonResponse:
        """Дополняет файл в хранилище файлом с тем же именем, представленным `str`"""
        pass

    def removeFile(self, id: str, filename: str) -> JsonResponse:
        """Удаляет файл c именем `filename` из хранилища"""
        pass

    def readFile(self, id: str, filename: str) -> JsonResponse:
        """Считывает файл c именем `filename` из хранилища"""
        pass

    def listFiles(self, id: str) -> JsonResponse:
        """Получает информацию о файлах в окружении"""
        pass

    def generate(self, id: str, prompt: str) -> JsonResponse:
        """Генерирует текстовый файл на основе файлов окружения"""
        pass

    def sendPrompt(self, id: str, prompt: str) -> JsonResponse:
        """Отправляет запрос модели"""
        pass

    def commitFiles(self, id: str, prompt: str) -> JsonResponse:
        """Загружает файлы окружения в контекст модели"""
        pass

    def getContext(self, id: str, prompt: str) -> JsonResponse:
        """Получает контекст модели по идентификатору окружения"""
        pass

    def clearContext(self, id: str, prompt: str) -> JsonResponse:
        """Очищает контекст модели"""
        pass