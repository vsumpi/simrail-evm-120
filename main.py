import sys
import requests
import serial
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QDialog,
    QPushButton,
    QComboBox,
    QFormLayout,
    QMessageBox,
)
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QFont
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

# URL Construrctor
base_url = "https://panel.simrail.eu:8084"
servers_url = f"{base_url}/servers-open"
trains_url_template = f"{base_url}/trains-open?serverCode="

# Arduino coms
def sendMessage(signal):
    try:
        with serial.Serial('COM3', 57600, timeout=5) as ser:
            print(f"Serial Communication: {signal} -> {ser.name}")
            ser.read()
            ser.write(f" {signal}\n".encode())
    except Exception as e:
        print(f"Serial communication failed: {e}")

sendMessage("OK")


class StartupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EVM120")
        self.servers = []
        self.init_ui()
        self.fetch_servers()

    def init_ui(self):
        layout = QFormLayout()

        self.server_combo = QComboBox()
        self.server_combo.currentIndexChanged.connect(self.fetch_trains)
        layout.addRow("Select Server:", self.server_combo)

        self.train_combo = QComboBox()
        layout.addRow("Select Train:", self.train_combo)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_application)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def fetch_servers(self):
        try:
            response = requests.get(servers_url)
            if response.status_code == 200:
                print("Fetching servers...")
                servers_data = response.json().get("data", [])
                self.servers = [server for server in servers_data if server["IsActive"]]
                self.server_combo.clear()
                for server in self.servers:
                    print(f"Fetched server: {server['ServerName']}")
                    self.server_combo.addItem(
                        f"{server['ServerName']}", server["ServerCode"]
                    )
            else:
                QMessageBox.warning(self, "Error", "Failed to fetch servers.")
        except Exception as e:
            print(f"Exception occurred during server request: {str(e)}")
            QMessageBox.warning(
                self, "Error", "Exception occurred during server request."
            )

    def fetch_trains(self):
        server_code = self.server_combo.currentData()
        print(f"Fetching trains from server: {server_code}")
        if not server_code:
            return
        try:
            response = requests.get(f"{trains_url_template}{server_code}")
            if response.status_code == 200:
                trains = response.json().get("data", [])
                self.train_combo.clear()
                for train in trains:
                    print(f"Fetched train: {train['TrainNoLocal']}")
                    self.train_combo.addItem(train["TrainNoLocal"])
            else:
                QMessageBox.warning(self, "Error", "Failed to fetch trains.")
        except Exception as e:
            print(f"Exception occurred during train request: {str(e)}")
            QMessageBox.warning(
                self, "Error", "Exception occurred during train request."
            )

    def start_application(self):
        server_code = self.server_combo.currentData()
        train_number = self.train_combo.currentText()
        if server_code and train_number:
            self.server_code = server_code
            self.train_number = train_number
            self.accept()
        else:
            QMessageBox.warning(
                self, "Invalid Input", "Please select a valid server and train."
            )
class DVJ:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.label_text = "5×7 Matrix"

    def draw(self, painter):
        # Draw outer black box
        painter.setBrush(QBrush(QColor("black")))
        painter.drawRect(self.x, self.y, 140, 80)

    def dspeed(self, painter, text):
        self.label_text = text
        # Draw label inside the box (optional)
        painter.setPen(QColor("red"))
        painter.setFont(QFont('5X7 Matrix',28))
        painter.drawText(self.x + 25 , self.y + 60, self.label_text)

class SignalLight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lamp_colors = ["lime", "orange", "red", "orange", "white"]
        self.lights = [False] * len(self.lamp_colors)  # False = off, True = on

    def set_aspect(self, *on_indices):
        # print(f"Setting lamps at indices: {on_indices}")
        self.lights = [i in on_indices for i in range(len(self.lamp_colors))]
        # print(f"Resulting lights state: {self.lights}")

    def draw(self, painter):
        painter.setBrush(QBrush(QColor("black")))
        painter.drawRoundedRect(self.x, self.y, 40, 140, 10, 10)

        for i, (lamp_colors, is_on) in enumerate(zip(self.lamp_colors, self.lights)):
            color = QColor(lamp_colors) if is_on else QColor("grey")
            painter.setBrush(QBrush(color, Qt.SolidPattern))
            painter.drawEllipse(self.x + 10 , 10 + i * 25, 20, 20)


class TransparentWindow(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        self.signal_light.draw(painter)
        self.dvj.draw(painter)
        self.dvj.dspeed(painter, "---")

    def __init__(self, server_code, train_number):
        super().__init__()
        self.server_code = server_code
        self.train_number = train_number
        self.url = f"{trains_url_template}{server_code}"

        self.signal_light = SignalLight(x=0, y=0)
        self.dvj = DVJ(x=45, y=0)

        self.setWindowTitle("EVM120")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_api_data)
        self.timer.start(5000)

        self.old_pos = None

    def init_ui(self):
        layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)
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
                        signal_data = {"NextSignalSpeed": next_signal_speed}
                        print(f"Signal Reading: {signal_data['NextSignalSpeed']}")
                        break

                if signal_data:
                    signal = SignalLight(0, 0)
                    speed = signal_data["NextSignalSpeed"]
                    # sendMessage(str(speed))
                    if speed == 0:
                        self.signal_light.set_aspect(2)
                        self.update()
                        # self.load_image("speed_0.gif")
                    elif speed in [40, 60]:
                        self.signal_light.set_aspect(1, 3)
                        self.update()
                        # self.load_image("speed_40.gif")
                    elif speed in [80, 100]:
                        self.signal_light.set_aspect(0, 3)
                        self.update()
                        # self.load_image("speed_80.gif")
                    elif speed > 100:
                        # sendMessage("MAX")
                        self.signal_light.set_aspect(0)
                        self.update()
                        # self.load_image("speed_high.gif")
                    else:
                        self.clear_image()
        except Exception as e:
            print(f"Exception occurred during API request: {str(e)}")
            self.clear_image()

    def load_image(self, image_path):
        pixmap = QPixmap(image_path).scaled(
            self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    startup_dialog = StartupDialog()
    print("Starting Application...")
    if startup_dialog.exec_() == QDialog.Accepted:
        print(f"Selected: {startup_dialog.server_code} : {startup_dialog.train_number}")
        server_code = startup_dialog.server_code
        train_number = startup_dialog.train_number

        transparent_window = TransparentWindow(server_code, train_number)
        transparent_window.setGeometry(100, 100, 300, 250)
        transparent_window.show()

        sys.exit(app.exec_())
