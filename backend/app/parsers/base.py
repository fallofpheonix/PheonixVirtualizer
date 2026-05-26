from abc import ABC, abstractmethod
from typing import List
from ..models.types import ParseResult, ParseRequest

class BaseParser(ABC):
    @abstractmethod
    def parse(self, request: ParseRequest) -> ParseResult:
        pass

    @abstractmethod
    def supports_language(self, language: str) -> bool:
        pass
