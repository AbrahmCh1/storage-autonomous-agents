from typing import Callable, Any
import socket
import json

class EventEmitter():
    def __init__(self):
        self.event_handlers: dict[str, list[Callable[[str], Any]]] = {}
        # initialize the TCP connection

        return

        # Configura el socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 65432))
        self.sock.listen()

        print("Esperando conexión...")
        self.conn, self.addr = self.sock.accept()

        if self.conn:
            print('Conectado por', self.addr)


    def register_handler(self, type: str, handler: Callable[[str], Any]):
        if type not in self.event_handlers:
            self.event_handlers[type] = []

        self.event_handlers[type].append(handler)

    def send_event(self, type: str, data: Any):
        # send an event through current TCP connection with the following shape
        # {"type": type, "data": {...}}
        return

        event = {
            "type": type,
            "data": data
        }

        message = json.dumps(event).encode('utf-8')
        self.conn.sendall(message)
