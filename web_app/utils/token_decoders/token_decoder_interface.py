from abc import ABC, abstractmethod


class TokenDecoder(ABC):
    @abstractmethod
    def decode(self, token: str) -> dict:
        pass
