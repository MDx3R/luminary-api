import os
from typing import Iterator, List, overload
from abc import ABC, abstractmethod

from .connection import FTPConnection

# Create your managers here.

class FileManager(ABC):
    """
    Предоставляет интерфейс для классов файловых менеджеров
    """
    
    @abstractmethod
    def list(self, path: str) -> List[str]:
        """Выводит список имен в директории, указанной в path"""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Проверяет существование директории или файл по пути path"""
        pass

    @abstractmethod
    def makeDir(self, path: str) -> bool:
        """Создает директорию, указанную в path"""
        pass

    @abstractmethod
    def removeDir(self, path: str) -> bool:
        """Удаляет директорию, указанною в path"""
        pass

    @abstractmethod
    def clearDir(self, path: str) -> bool:
        """Очищает директорию, указанною в path"""
        pass

    @abstractmethod
    def readFile(self, path: str, name: str) -> str: # добавить возможность возврата генератора
        """Читает файл с именем name в директории path"""
        pass

    @overload
    @abstractmethod
    def saveFile(self, path: str, name: str, data: str, returning=False):
        """
        Создает файл с именем name в директории path и записывает в него data целиком
        """
        pass

    @overload
    @abstractmethod
    def saveFile(self, path: str, name: str, data: bytes, returning=False):
        """
        Создает файл с именем name в директории path и записывает в него data целиком
        """
        pass
    
    @overload
    @abstractmethod
    def saveFile(self, path: str, name: str, data: Iterator[bytes], returning=False):
        """
        Создает файл с именем name в директории path и записывает в него data по частям
        """
        pass

    @abstractmethod
    def removeFile(self, path: str, name: str) -> bool:
        """Удаляет файл с именем name в директории path"""
        pass

class LocalFileManager(FileManager):
    """
    Отвечает за хранение файлов локально
    """

    def __init__(self, basePath: str = ''):
        self.basePath = basePath

class RemoteFileManager(FileManager):
    """
    Отвечает за хранение файлов удаленно
    """

    def __init__(self):
        self.connection = FTPConnection()