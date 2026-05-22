"""Event Bus and CQRS base classes."""

from typing import Any, Callable, Dict, List, Type


class Message:
    """Base message type."""
    pass


class Command(Message):
    """Command changes state."""
    pass


class Event(Message):
    """Event indicates something happened."""
    pass


class Query(Message):
    """Query requests data without changing state."""
    pass


class EventBus:
    """Simple in-memory event bus and command/query dispatcher."""

    def __init__(self):
        self.handlers: Dict[Type[Message], List[Callable]] = {}

    def subscribe(self, message_type: Type[Message], handler: Callable) -> None:
        if issubclass(message_type, (Command, Query)):
            self.handlers[message_type] = [handler]
        else:
            if message_type not in self.handlers:
                self.handlers[message_type] = []
            if handler not in self.handlers[message_type]:
                self.handlers[message_type].append(handler)

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        for handler in self.handlers.get(type(event), []):
            handler(event)

    def execute(self, command: Command) -> Any:
        """Execute a command using its registered handler."""
        handlers = self.handlers.get(type(command), [])
        if not handlers:
            raise ValueError(f"No handler registered for command {type(command).__name__}")
        if len(handlers) > 1:
            raise ValueError(f"Multiple handlers registered for command {type(command).__name__}")
        return handlers[0](command)

    def query(self, query: Query) -> Any:
        """Execute a query using its registered handler."""
        handlers = self.handlers.get(type(query), [])
        if not handlers:
            raise ValueError(f"No handler registered for query {type(query).__name__}")
        if len(handlers) > 1:
            raise ValueError(f"Multiple handlers registered for query {type(query).__name__}")
        return handlers[0](query)

# Global singleton bus for simple use cases
bus = EventBus()
