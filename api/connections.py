from openai import OpenAI

from .base import once, Singleton

# Create and configure your connections here.

class Connection(Singleton):
    """
    Базовый класс подключений
    """
    pass

class RedisConnection(Connection):
    """
    Класс покдлючения Redis
    """
    @once
    def __init__(self, host: str, port: int):
        self.client = None

class FTPConnection(Connection):
    """
    Класс покдлючения FTP-серверу
    """
    pass

class GPTConnection(Connection):
    """
    Класс покдлючения ChatGPT
    """

    model: str = None

    @once
    def __init__(self, api_key: str, url: str, model: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url=url,
            timeout=30
        )
        self.model = model