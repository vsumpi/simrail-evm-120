# --- IMPORTS ---
from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from PyQt5.QtWebSockets import QWebSocket
import json

# --- CONSTANTS ---
PROTOCOL = "ws"
IP = "localhost"
PORT = 5556
ROUTE = "ws"

# --- API CLASS ---
class TelemetryClient(QObject):

    error_occurred = pyqtSignal(object)
    block_speed = pyqtSignal(int)
    next_block_speed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.client = QWebSocket()
        self.client.textMessageReceived.connect(self.on_message)
        self.client.error.connect(self.on_error)

    def start(self):
        print(f"Connecting to SimrailConnect WebSocket on {PROTOCOL}://{IP}:{PORT}/{ROUTE}")
        self.client.open(QUrl(f"{PROTOCOL}://{IP}:{PORT}/{ROUTE}"))

    def stop(self):
        self.client.close()

    def on_message(self, message):
        try:
            data = json.loads(message)

            if "hasSignal" in data and data["hasSignal"] is True:
                name = data.get("name", "Unknown")
                speed_limit = data.get("speedLimitKmh")
                next_speed_limit = data.get("nextSpeedLimitKmh")

                if speed_limit is not None:
                    self.block_speed.emit(int(speed_limit))
                if next_speed_limit is not None:
                    self.next_block_speed.emit(int(next_speed_limit))


        except Exception as e:
            self.error_occurred.emit(f"Internal Parse Error: {str(e)}")

    def on_error(self, error_code):
        error_msg = self.client.errorString()
        self.error_occurred.emit(f"WebSocket Network Error: {error_msg}")
        self.client.close()