from typing import Callable, Any
import socket
import json
import threading

class MockEmitter():
    def __init__(self):
        pass

    def register_handler(self, type: str, handler: Callable[[str], Any]):
        pass

    def send_event(self, type: str, data: Any):
        pass

    def close(self):
        pass

class EventEmitter():
    def __init__(self):
        self.event_handlers: dict[str, list[Callable[[str], Any]]] = {}
        # Configura el socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 65432))
        self.sock.listen()

        print("Esperando conexión...")
        self.conn, self.addr = self.sock.accept()

        if self.conn:
            print('Connected by', self.addr)
            # Create a thread for listening
            self.listen_thread = threading.Thread(target=self._start_listening)
            self.listen_thread.daemon = True  # Thread will exit when main program exits
            self.listen_thread.start()

    def _start_listening(self):
        buffer = ""
        while True:
            try:
                data = self.conn.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    try:
                        event = json.loads(message)
                        if event['type'] in self.event_handlers:
                            data = event['data'].split(',')
                            for handler in self.event_handlers[event['type']]:
                                handler(data)
                    except json.JSONDecodeError:
                        print("Error decoding JSON message")

            except Exception as e:
                print(f"Error in listening thread: {e}")
                break

    def register_handler(self, type: str, handler: Callable[[str], Any]):
        if type not in self.event_handlers:
            self.event_handlers[type] = []

        self.event_handlers[type].append(handler)

    def send_event(self, type: str, data: Any):
        # send an event through current TCP connection with the following shape
        # {"type": type, "data": {...}}
        str_data = [str(d) for d in data]

        event = {
            "type": type,
            "data": ",".join(str_data)
        }

        message = json.dumps(event) + "\n"
        self.conn.sendall(message.encode('utf-8'))

    def close(self):
        # Update close method to handle thread cleanup
        if hasattr(self, 'conn'):
            self.conn.close()
        if hasattr(self, 'sock'):
            self.sock.close()
