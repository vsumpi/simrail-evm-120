import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QDialog, QLineEdit, QPushButton, QComboBox, QFormLayout, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt, QPoint

# Define the base URLs
base_url = 'https://panel.simrail.eu:8084'
servers_url = f'{base_url}/servers-open'
trains_url_template = f'{base_url}/trains-open?serverCode='

class StartupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Startup Menu')
        self.setGeometry(100, 100, 300, 200)
        self.servers = []
        self.init_ui()
        self.fetch_servers()

    def init_ui(self):
        layout = QFormLayout()

        self.server_combo = QComboBox()
        self.server_combo.currentIndexChanged.connect(self.fetch_trains)
        layout.addRow('Select Server:', self.server_combo)

        self.train_combo = QComboBox()
        layout.addRow('Select Train:', self.train_combo)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_application)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def fetch_servers(self):
        try:
            response = requests.get(servers_url)
            if response.status_code == 200:
                servers_data = response.json().get('data', [])
                self.servers = [server for server in servers_data if server['IsActive']]
                self.server_combo.clear()
                for server in self.servers:
                    self.server_combo.addItem(f"{server['ServerName']} ({server['ServerCode']})", server['ServerCode'])
            else:
                QMessageBox.warning(self, 'Error', 'Failed to fetch servers.')
        except Exception as e:
            print(f"Exception occurred during server request: {str(e)}")
            QMessageBox.warning(self, 'Error', 'Exception occurred during server request.')

    def fetch_trains(self):
        server_code = self.server_combo.currentData()
        if not server_code:
            return
        
        try:
            response = requests.get(f'{trains_url_template}{server_code}')
            if response.status_code == 200:
                trains = response.json().get('data', [])
                self.train_combo.clear()
                for train in trains:
                    self.train_combo.addItem(train['TrainNoLocal'])
            else:
                QMessageBox.warning(self, 'Error', 'Failed to fetch trains.')
        except Exception as e:
            print(f"Exception occurred during train request: {str(e)}")
            QMessageBox.warning(self, 'Error', 'Exception occurred during train request.')

    def start_application(self):
        server_code = self.server_combo.currentData()
        train_number = self.train_combo.currentText()
        
        if server_code and train_number:
            self.server_code = server_code
            self.train_number = train_number
            self.accept()
        else:
            QMessageBox.warning(self, 'Invalid Input', 'Please select a valid server and train.')

class TransparentWindow(QWidget):
    def __init__(self, server_code, train_number):
        super().__init__()
        
        self.server_code = server_code
        self.train_number = train_number
        self.url = f'{trains_url_template}{server_code}'
        
        self.setWindowTitle('Next Signal Information')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.init_ui()
        
        # Setup timer to fetch API data every 5 seconds (5000 milliseconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_api_data)
        self.timer.start(5000)
        
        self.old_pos = None
        
    def init_ui(self):
        layout = QVBoxLayout()
        
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
                            "NextSignalSpeed": next_signal_speed,
                        }
                        break
                
                if signal_data:
                    # Check next signal speed and display corresponding image
                    if signal_data['NextSignalSpeed'] == 0:
                        self.load_image("speed_0.gif")
                    elif signal_data['NextSignalSpeed'] == 40:
                        self.load_image("speed_40.gif")
                    elif signal_data['NextSignalSpeed'] == 60:
                        self.load_image("speed_40.gif")
                    elif signal_data['NextSignalSpeed'] == 80:
                        self.load_image("speed_80.gif")
                    elif signal_data['NextSignalSpeed'] == 100:
                        self.load_image("speed_80.gif")
                    elif signal_data['NextSignalSpeed'] >100:
                        self.load_image("speed_high.gif")
                    else:
                        self.clear_image()
                    
                else:
                    self.clear_image()
            
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
    if startup_dialog.exec_() == QDialog.Accepted:
        server_code = startup_dialog.server_code
        train_number = startup_dialog.train_number
        
        transparent_window = TransparentWindow(server_code, train_number)
        transparent_window.setGeometry(100, 100, 300, 250)  # Set initial window position and size
        transparent_window.show()
    
        sys.exit(app.exec_())
