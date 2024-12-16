import os
from typing import Iterator, List, Union, Dict
from abc import ABC, abstractmethod

from .connections import FTPConnection

# Create your managers here.

def fileStatFactory(filename: str, size: int, updatedAt: int):
    return {
        "filename": filename,
        "size": size,
        "updatedAt": updatedAt
    }

class FileManager(ABC):
    """
    Предоставляет интерфейс для классов файловых менеджеров
    """
    
    @abstractmethod
    def list(self, path: str) -> List[str]:
        """Выводит список имен в директории, указанной в path"""
        pass

    @abstractmethod
    def listFiles(self, path: str) -> List[str]:
        """Выводит список имен файлов в директории, указанной в path"""
        pass

    @abstractmethod
    def listFilesStat(self, path: str) -> List[Dict]:
        """Выводит список сведений о файлах в директории, указанной в path"""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Проверяет существование директории или файл по пути path"""
        pass

    @abstractmethod
    def makeDir(self, path: str) -> None:
        """Создает директорию, указанную в path"""
        pass

    @abstractmethod
    def removeDir(self, path: str) -> None:
        """Удаляет директорию, указанною в path"""
        pass

    @abstractmethod
    def clearDir(self, path: str) -> None:
        """Очищает директорию, указанною в path"""
        pass

    @abstractmethod
    def readFile(self, path: str, name: str) -> str: # добавить возможность возврата генератора
        """Читает файл с именем name в директории path"""
        pass
    
    @abstractmethod
    def saveFile(self, path: str, name: str, data: str) -> None:
        """
        Создает файл с именем name в директории path и записывает в него data целиком
        """
        pass

    @abstractmethod
    def saveFileByChunks(self, path: str, name: str, data: Iterator[bytes]) -> None:
        """
        Создает файл с именем name в директории path и записывает в него data по частям
        """
        pass

    @abstractmethod
    def removeFile(self, path: str, name: str) -> None:
        """Удаляет файл с именем name в директории path"""
        pass

class LocalFileManager(FileManager):
    """
    Отвечает за хранение файлов локально
    """

    def __init__(self, basePath: str = ''):
        self.basePath = basePath
        self.__initializeBaseDir()

    def __initializeBaseDir(self):
        if (os.path.exists(self.basePath) == False):
            currentPath = ''
            for x in self.basePath.split('/'):
                currentPath +=x
                if (os.path.exists(currentPath) == False):
                    os.mkdir(path=x)
                currentPath+='/'

    def makePath(self, path: str, name: str = "") -> str:
        return f'{self.basePath}/{path}{f"/{name}" if name else ""}'

    def list(self, path: str) -> List[str]:
        """Выводит список имен в директории, указанной в path"""

        return os.listdir(self.makePath(path))

    def listFiles(self, path: str) -> List[str]:
        """Выводит список имен файлов в директории, указанной в path"""
        result = []
        for name in self.list(path):
            if (os.path.isdir(self.makePath(path, name))): # This means name is dir
                continue

            result.append(name)

        return result

    def listFilesStat(self, path: str) -> List[Dict]:
        """Выводит список сведений о файлах в директории, указанной в path"""
        result = []
        for name in self.list(path):
            fullPath = self.makePath(path, name)
            if (os.path.isdir(fullPath)): # This means name is dir
                continue

            stat = os.stat(fullPath)
            result.append(
                fileStatFactory(
                    name, 
                    stat.st_size, 
                    int(stat.st_mtime)
                )
            )

        return result

    def exists(self, path: str) -> bool:
        """Проверяет существование директории или файл по пути path"""
        return os.path.exists(self.makePath(path))

    def makeDir(self, path: str) -> None:
        """Создает директорию, указанную в path"""
        os.mkdir(self.makePath(path))

    def removeDir(self, path: str) -> None:
        """Удаляет директорию, указанную в path"""
        os.rmdir(self.makePath(path))

    def clearDir(self, path: str) -> None:
        """Очищает директорию, указанною в path"""
        for name in self.list(path):
            fullPath = self.makePath(path, name)
            if (os.path.isdir(fullPath)):
                self.removeDir()
            else:
                self.removeFile(fullPath)

    def readFile(self, path: str, name: str) -> str:
        """Читает файл с именем name в директории path"""
        with open(self.makePath(path, name), "r", encoding="utf-8") as file:
            return file.read()
        
    def saveFile(self, path: str, name: str, data: str) -> None:
        """
        Создает файл с именем name в директории path и записывает в него data целиком
        """
        with open(self.makePath(path, name), "wb+") as file:
            file.write(data)

    def saveFileByChunks(self, path: str, name: str, data: Iterator[bytes]) -> None:
        """
        Создает файл с именем name в директории path и записывает в него data по частям
        """
        with open(self.makePath(path, name), "wb+") as file:
            for x in data:
                file.write(x)

    def removeFile(self, path: str, name: str) -> None:
        """Удаляет файл с именем name в директории path"""
        os.remove(self.makePath(path, name))

class RemoteFileManager(FileManager):
    """
    Отвечает за хранение файлов удаленно
    """

    def __init__(self, basePath: str = ''):
        self.basePath = basePath
        self.connection = FTPConnection()