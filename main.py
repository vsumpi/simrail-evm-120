import sys
import requests
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QDialog, QPushButton, QComboBox, QFormLayout, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt

# URL Construrctor
base_url = 'https://panel.simrail.eu:8084'
servers_url = f'{base_url}/servers-open'
trains_url_template = f'{base_url}/trains-open?serverCode='

# Ardino coms
def sendMessage(signal):
    try:
        with serial.Serial('COM3', 57600, timeout=5) as ser:
            print(f"Serial Communication: {signal} -> {ser.name}")
            ser.read()
            ser.write(f" {signal}\n".encode())
            ser.close()
    except:
        exit
sendMessage("OK")

class StartupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('EVM120') # Set WindowTitle
        self.servers = [] # Create Array for ServerList
        self.init_ui() # Init UI: Make Layout
        self.fetch_servers() # Fetch ServerList from SimRail servers

    def init_ui(self):
        # We create a Form to display our data
        layout = QFormLayout() # New FormLayout
        
        self.server_combo = QComboBox() # Dropdown
        self.server_combo.currentIndexChanged.connect(self.fetch_trains) # Update dropdown values
        layout.addRow('Select Server:', self.server_combo) # Select Server: [Dropdown]

        self.train_combo = QComboBox() # Dropdown
        layout.addRow('Select Train:', self.train_combo) # Select Train: [Dropdown]

        self.start_button = QPushButton('Start') # Button
        self.start_button.clicked.connect(self.start_application) # Start Application
        layout.addWidget(self.start_button) # [Button]

        self.setLayout(layout) # Render Layout

    def fetch_servers(self):
        try:
            response = requests.get(servers_url) # Get the ServerList
            if response.status_code == 200: # 200 = OK
                print("Fetching servers...")
                servers_data = response.json().get('data', []) # Store data as array
                self.servers = [server for server in servers_data if server['IsActive']] # Set ServerList from data
                self.server_combo.clear() # Clear [Dropdown]
                for server in self.servers:
                    print(f"Fetched server: {server['ServerName']}")
                    self.server_combo.addItem(f"{server['ServerName']}", server['ServerCode']) # Add items to [Dropdown]
            else:
                # Error handling
                QMessageBox.warning(self, 'Error', 'Failed to fetch servers.')
        except Exception as e:
            print(f"Exception occurred during server request: {str(e)}")
            QMessageBox.warning(self, 'Error', 'Exception occurred during server request.')

    def fetch_trains(self):
        server_code = self.server_combo.currentData() # Fetch Selected from [Dropdown]
        print(f"Fetching trains from server: {server_code}")
        if not server_code:
            return
        try:
            response = requests.get(f'{trains_url_template}{server_code}') # Fetch Train list from [Dropdown] server
            if response.status_code == 200:
                trains = response.json().get('data', []) # Store data in array
                self.train_combo.clear() # Clear [Dropdown]
                for train in trains:
                    print(f"Fetched train: {train['TrainNoLocal']}")
                    self.train_combo.addItem(train['TrainNoLocal']) # Add items to [Dropdown] 
            else:
                # Error handling
                QMessageBox.warning(self, 'Error', 'Failed to fetch trains.')
        except Exception as e:
            print(f"Exception occurred during train request: {str(e)}")
            QMessageBox.warning(self, 'Error', 'Exception occurred during train request.')

    def start_application(self):
        server_code = self.server_combo.currentData() # Set ServerCode
        train_number = self.train_combo.currentText() # Set TrainNumber
        
        # Is train available?
        if server_code and train_number:
            self.server_code = server_code
            self.train_number = train_number
            self.accept()
        else:
            # Error handling
            QMessageBox.warning(self, 'Invalid Input', 'Please select a valid server and train.')

class TransparentWindow(QWidget):
    def __init__(self, server_code, train_number):
        super().__init__()
        
        self.server_code = server_code 
        self.train_number = train_number
        self.url = f'{trains_url_template}{server_code}'
        
        self.setWindowTitle('EVM120') # Set WindowTitle
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) # Set Frameless | AlwaysOnTop
        self.setAttribute(Qt.WA_TranslucentBackground) # Set Transparent window
        
        self.init_ui()
        
        # Setup timer to fetch API data every 5 seconds (5000 milliseconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_api_data)
        self.timer.start(5000)
        
        self.old_pos = None
        
    def init_ui(self):
        layout = QVBoxLayout() # Vertically Stacked Layout
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)  # Set a fixed size for the image label
        layout.addWidget(self.image_label)
        
        self.setLayout(layout)
        
    def fetch_api_data(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                data = response.json()
                
                signal_data = None
                
                for train in data.get("data", []):
                    if train.get("TrainNoLocal") == self.train_number:
                        train_data = train.get("TrainData", {})
                        next_signal_speed = train_data.get("SignalInFrontSpeed", 0)
                        signal_data = {
                            "NextSignalSpeed": next_signal_speed
                        }
                        print(f"Signal Reading: {signal_data['NextSignalSpeed']}")
                        break
                
                if signal_data:
                    # Check next signal speed and display corresponding image
                    if signal_data['NextSignalSpeed'] == 0:
                        sendMessage(int(signal_data['NextSignalSpeed']))
                        self.load_image("speed_0.gif")
                    elif signal_data['NextSignalSpeed'] == 40:
                        sendMessage(int(signal_data['NextSignalSpeed']))
                        self.load_image("speed_40.gif")
                    elif signal_data['NextSignalSpeed'] == 60:
                        sendMessage(int(signal_data['NextSignalSpeed']))
                        self.load_image("speed_40.gif")
                    elif signal_data['NextSignalSpeed'] == 80:
                        sendMessage(int(signal_data['NextSignalSpeed']))
                        self.load_image("speed_80.gif")
                    elif signal_data['NextSignalSpeed'] == 100:
                        sendMessage(int(signal_data['NextSignalSpeed']))
                        self.load_image("speed_80.gif")
                    elif signal_data['NextSignalSpeed'] >100:
                        sendMessage("MAX")
                        self.load_image("speed_high.gif")
                    else:
                        self.clear_image()
        
        except Exception as e:
            print(f"Exception occurred during API request: {str(e)}")
            self.clear_image()
    
    def load_image(self, image_path):
        pixmap = QPixmap(image_path).scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
    
    def clear_image(self):
        self.image_label.clear()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.pos() - self.old_pos
            self.move(self.pos() + delta)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    startup_dialog = StartupDialog()
    print("Starting Apllication...")
    if startup_dialog.exec_() == QDialog.Accepted:
        print(f"Selected: {startup_dialog.server_code} : {startup_dialog.train_number}")
        server_code = startup_dialog.server_code
        sendMessage(server_code)
        train_number = startup_dialog.train_number
        sendMessage(train_number)
        
        transparent_window = TransparentWindow(server_code, train_number)
        transparent_window.setGeometry(100, 100, 300, 250)  # Set initial window position and size
        transparent_window.show()
    
        sys.exit(app.exec_())
