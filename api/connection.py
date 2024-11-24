from openai import OpenAI

from .base import once, Singleton

# Create and configure your connections here.

class Connection(Singleton):
    """
    Базовый класс подключений
    """
    pass

class FTPConnection(Connection):
    """
    Класс покдлючения FTP-серверу
    """
    pass

class GPTConnection(Connection):
    """
    Класс покдлючения ChatGPT
    """
    @once
    def __init__(self, api_key: str, url: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url=url,
            timeout=30
        )

    