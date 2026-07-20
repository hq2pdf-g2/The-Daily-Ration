from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCollector(ABC):
    @abstractmethod
    def fetch_raw_data(self) -> List[Dict[str, Any]]:
        """Fetch raw articles from the source."""
        pass

    @abstractmethod
    def parse_content(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean HTML, extract title, body, author, and date."""
        pass