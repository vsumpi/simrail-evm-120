# Find access and resources at https://wiki.simrail.eu/en/API/API-Introduction

# --- IMPORTS ---
from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from PyQt5.QtWebSockets import QWebSocket
import json
# from PyQt5.QtWidgets import *
# import requests
# from functools import wraps

'''
# --- URLs ---

BASE_URL = "https://panel.simrail.eu"
BASE_PORT = 8084
GET_SERVER_LIST_URL = f"{BASE_URL}:{BASE_PORT}/servers-open"
GET_TRAINDATA_URL = f"{BASE_URL}:{BASE_PORT}/trains-open?serverCode="

# --- DECORATOR ---


def api_safety_net(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            print(f'Modul  "{func.__name__}" was called')
            return func(self, *args, **kwargs)
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Network error: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"Internal Error in {func.__name__}: {str(e)}")

    return wrapper
'''

# --- API CLASS ---
class FetchData(QObject):

    # Creating signals to send data back for UI
    error_occurred = pyqtSignal(object)  # errors
    speed_limit_loaded = pyqtSignal(int) # # Telemetry for UI
    next_speed_limit_loaded = pyqtSignal(int) # # Telemetry for UI

    def __init__(self, parent = ...):
        super().__init__(self)
        self.client = QWebSocket()

        self.client.textMessageReceived.connect(self.on_message)
        self.client.error.connect(self.on_error)

    def start_telemetry(self):
        print("Connecting to SimrailConnect WebSocket...")
        self.client.open(QUrl("ws://localhost:5556/ws"))

    def on_message(self, message):
        try:
            data = json.loads(message)
            if "speedLimitKmh" in data:
                self.speed_limit_loaded.emit(int(data["speedLimitKmh"]))
            if "nextSpeedLimitKmh" in data:
                self.next_speed_limit_loaded.emit()
        except Exception as e:
            self.error_occurred.emit(f"Internal Parse Error: {str(e)}")

    def on_error(self, error_code):
        self.error_occurred.emit(f"WebSocket Network Error: {self.client.errorString()}")


    '''
    FOR API calls
    servers_loaded = pyqtSignal(list)  # Online servers
    trains_loaded = pyqtSignal(list)  # Running trains by number
    speed_limit_loaded = pyqtSignal(int)  # Telemetry for UI
    '''
    
    '''
    API calls
    def get_active_servers(self):
        response = requests.get(GET_SERVER_LIST_URL, timeout=5)
        if response.status_code == 200:
            raw_servers_data = response.json().get("data", [])  # Raw JSON response
            active_servers = [
                s for s in raw_servers_data if s.get("IsActive")
            ]  # FILTER with List Comprehension
            self.servers_loaded.emit(active_servers)  # Send data to UI

    @api_safety_net
    def get_running_trains(self, server_code):
        response = requests.get(f"{GET_TRAINDATA_URL}{server_code}", timeout=5)
        if response.status_code == 200:
            raw_trains_data = response.json().get("data", [])  # Raw JSON response
            running_trains = [
                t["TrainNoLocal"] for t in raw_trains_data
            ]  # FILTER with List Comprehension
            self.trains_loaded.emit(running_trains)  # Send data to UI

    @api_safety_net
    def update_telemetry(self, server_code, train_no):
        response = requests.get(f"{GET_TRAINDATA_URL}{server_code}", timeout=5)
        if response.status_code == 200:
            raw_trains_data = response.json().get("data", [])
            cache = {
                t["TrainNoLocal"]: t for t in raw_trains_data
            }  # Dict Comprehension

            selected_train = cache.get(train_no)
            if selected_train:
                speed_limit = selected_train.get("Velocity", 0)
                self.speed_limit_loaded.emit(speed_limit)
    '''