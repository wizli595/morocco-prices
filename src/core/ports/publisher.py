"""Port: contract for message publishers."""

from abc import ABC, abstractmethod

from src.core.models.observation import RawObservation


class BasePublisher(ABC):
    """Publishes observations to a message bus."""

    @abstractmethod
    def publish(self, topic: str, observation: RawObservation) -> None:
        """Send a single observation to the given topic."""

    @abstractmethod
    def flush(self) -> None:
        """Ensure all pending messages are delivered."""
