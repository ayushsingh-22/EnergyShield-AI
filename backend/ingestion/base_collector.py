import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

from models.data_source_schema import RawSourceRecord

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """
    Abstract Base Class for all data collectors in EnergyShield AI.
    Ensures that all collectors implement the necessary methods to fetch,
    normalize, and report their health status gracefully.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def fetch(self) -> List[RawSourceRecord]:
        """
        Fetches data from the external source or seeded files, handles
        exceptions gracefully, and returns a list of RawSourceRecords.
        Never crashes the pipeline.
        """
        pass

    @abstractmethod
    def normalize(self, raw_data: Any) -> List[RawSourceRecord]:
        """
        Converts the raw payload into a list of RawSourceRecords.
        (Usually called internally by fetch(), or overridden if needed)
        """
        pass

    @abstractmethod
    def health(self) -> bool:
        """
        Checks if the external source or seed file is accessible.
        """
        pass

    def metadata(self) -> Dict[str, Any]:
        """
        Returns metadata about the collector.
        """
        return {
            "source_name": self.source_name,
            "collector_type": self.__class__.__name__,
            "last_initialized": datetime.utcnow().isoformat(),
        }
