from typing import Callable, Any

class EventEmitter():
    def __init__(self):
        self.event_handlers: dict[str, list[Callable[[str], Any]]] = {}
        # initialize the TCP connection

    def register_handler(self, type: str, handler: Callable[[str], Any]):
        if type not in self.event_handlers:
            self.event_handlers[type] = []

        self.event_handlers[type].append(handler)

    def send_event(self, type: str, data: Any):
        # send an event through current TCP connection with the following shape
        # {"type": type, "data": {...}}
        pass