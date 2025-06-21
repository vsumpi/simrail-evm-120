# --- IMPORTS ---
# Import necessary libraries.
import sys  # For system-specific parameters and functions, like exiting the app.
import requests  # For making HTTP requests to the web API.
import serial  # For serial communication (e.g., with an Arduino).
from PyQt5.QtWidgets import (
    QApplication,  # Manages the GUI application's control flow and main settings.
    QWidget,  # Base class for all user interface objects.
    QVBoxLayout,  # A layout manager that arranges widgets vertically.
    QLabel,  # A widget for displaying text or images.
    QDialog,  # A base class for dialog windows.
    QPushButton,  # A command button widget.
    QComboBox,  # A dropdown list widget.
    QFormLayout,  # A layout manager for two-column forms (e.g., "Label: [Widget]").
    QMessageBox,  # A dialog for showing messages (warnings, errors, info).
)
from PyQt5.QtGui import QPainter, QBrush, QFont, QColor, QIcon  # Classes for drawing.
from PyQt5.QtCore import Qt, QTimer  # Core Qt functionalities, including the timer.

# --- GLOBAL CONFIGURATION ---
# Base URL for the SimRail API.
base_url = "https://panel.simrail.eu:8084"
# Specific endpoint for fetching open servers.
servers_url = f"{base_url}/servers-open"
# A template for the URL to fetch trains, which requires a server code.
trains_url_template = f"{base_url}/trains-open?serverCode="


'''# --- ARDUINO COMMUNICATION ---
def sendMessage(signal):
    """
    Sends a string 'signal' to a device connected to the serial port 'COM3'.
    This is intended for communication with an Arduino or similar microcontroller.
    """
    try:
        # 'with' statement ensures the serial port is properly closed after use.
        with serial.Serial('COM3', 57600, timeout=5) as ser:
            print(f"Serial Communication: {signal} -> {ser.name}")
            ser.read()  # Read any existing data from the buffer.
            ser.write(f" {signal}\n".encode())  # Encode the string to bytes and send it.
    except Exception as e:
        # If communication fails (e.g., port not found, device disconnected), print an error.
        print(f"Serial communication failed: {e}")

# Send an initial "OK" message on startup to check the connection.
sendMessage("OK")'''


# --- STARTUP DIALOG ---
class StartupDialog(QDialog):
    """
    This dialog window appears on startup, allowing the user to select
    a game server and a train before the main application window opens.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EVM-120")
        self.setWindowIcon(QIcon('./images/logo.ico'))
        self.servers = []  # A list to store data about available servers.
        self.init_ui()  # Set up the user interface elements.
        self.fetch_servers()  # Immediately fetch server data to populate the dropdown.

    def init_ui(self):
        """Initializes the widgets and layout for the startup dialog."""
        layout = QFormLayout()

        # Dropdown for server selection.
        self.server_combo = QComboBox()
        self.server_combo.currentIndexChanged.connect(self.fetch_trains)  # Call fetch_trains when a server is selected.
        layout.addRow("Select Server:", self.server_combo)

        # Dropdown for train selection.
        self.train_combo = QComboBox()
        layout.addRow("Select Train:", self.train_combo)

        # Dropdown for display mode selection
        self.display_mode_combo = QComboBox()
        self.display_mode_combo.addItem("Both", "both")
        self.display_mode_combo.addItem("Signal Light", "signal_light")
        self.display_mode_combo.addItem("DVJ", "dvj")
        layout.addRow("Display Mode:", self.display_mode_combo)

        # Button to start the main application.
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_application)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def fetch_servers(self):
        """Fetches the list of active servers from the API and populates the server dropdown."""
        try:
            response = requests.get(servers_url)
            if response.status_code == 200:
                print("Fetching servers...")
                servers_data = response.json().get("data", [])
                # Filter for only active servers.
                self.servers = [server for server in servers_data if server["IsActive"]]
                self.server_combo.clear()
                for server in self.servers:
                    # Add each server to the dropdown, storing its ServerCode as data.
                    self.server_combo.addItem(f"{server['ServerName']}", server["ServerCode"])
            else:
                QMessageBox.warning(self, "Error", "Failed to fetch servers.")
        except Exception as e:
            print(f"Exception occurred during server request: {str(e)}")
            QMessageBox.warning(self, "Error", "Exception occurred during server request.")

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
                train_numbers = [train["TrainNoLocal"] for train in trains]
                """ INSERTION SORT v.2"""
                for i in range(1, len(train_numbers)):
                    j = i - 1
                    helper = train_numbers[i]
                    while j >= 0 and train_numbers[j] > train_numbers[j + 1]:
                        train_numbers[j], train_numbers[j + 1] = (
                            train_numbers[j + 1],
                            train_numbers[j],
                        )
                        j -= 1
                    helper = train_numbers[j + 1]

                for train in train_numbers:
                    print(f"Fetched train: {train}")
                    self.train_combo.addItem(train)
            else:
                QMessageBox.warning(self, "Error", "Failed to fetch trains.")
        except Exception as e:
            print(f"Exception occurred during train request: {str(e)}")

    def start_application(self):
        """
        Called when the 'Start' button is clicked. It validates the selections
        and, if valid, closes the dialog with an 'Accepted' status.
        """
        server_code = self.server_combo.currentData()
        train_number = self.train_combo.currentText()
        display_mode = self.display_mode_combo.currentData()

        if server_code and train_number:
            self.server_code = server_code
            self.train_number = train_number
            self.display_mode = display_mode # Store the selected display mode
            self.accept()  # This closes the dialog and returns QDialog.Accepted.
        else:
            QMessageBox.warning(self, "Invalid Input", "Please select a valid server and train.")

# --- DISPLAY WIDGETS ---

class DVJ:
    """
    A custom widget to display a digital speed value (like a 5x7 matrix display).
    """
    def __init__(self, x, y):
        self.x = x  # The x-coordinate of the widget.
        self.y = y  # The y-coordinate of the widget.
        self.label_text = "---"  # The initial text to display.

    def set_speed(self, text):
        """Updates the internal state (the text) of the widget."""
        self.label_text = str(text)

    def draw(self, painter):
        """Draws the widget using its current state."""
        # Draw the black background box.
        painter.setBrush(QBrush(QColor("black")))
        painter.drawRect(self.x, self.y, 130, 70)
        # Draw the text stored in self.label_text.
        painter.setPen(QColor("red"))
        painter.setFont(QFont('5X7 Matrix', 28))
        painter.drawText(self.x + 17, self.y + 55, self.label_text)


class SignalLight:
    """
    A custom widget to display a railway signal with multiple lamps.
    """
    def __init__(self, x, y):
        self.x = x  # The x-coordinate of the widget.
        self.y = y  # The y-coordinate of the widget.
        # Define the colors of the lamps from top to bottom.
        self.lamp_colors = ["lime", "orange", "red", "orange", "white"]
        # A list of booleans to track which lamps are on (True) or off (False).
        self.lights = [False] * len(self.lamp_colors)

    def set_aspect(self, *on_indices):
        """Sets which lights are on based on their indices."""
        self.lights = [i in on_indices for i in range(len(self.lamp_colors))]

    def draw(self, painter):
        """Draws the signal housing and all the lamps based on their on/off state."""
        # Draw the black signal housing.
        painter.setBrush(QBrush(QColor("black")))
        painter.drawRoundedRect(self.x, self.y, 40, 140, 10, 10)
        # Iterate through the lamps and draw each one.
        for i, (lamp_color, is_on) in enumerate(zip(self.lamp_colors, self.lights)):
            # Choose the lamp's color: its actual color if 'on', or grey if 'off'.
            color = QColor(lamp_color) if is_on else QColor("grey")
            painter.setBrush(QBrush(color, Qt.SolidPattern))
            painter.drawEllipse(self.x + 10, 10 + i * 25, 20, 20)


# --- MAIN APPLICATION WINDOW ---
class TransparentWindow(QWidget):
    """
    The main application window. It's frameless, stays on top, and has a transparent background.
    It acts as a controller, fetching data and telling the display widgets how to update.
    """
    def paintEvent(self, event):
        """
        This is a special PyQt method that is called automatically whenever the window
        needs to be redrawn. Its only job is to tell the child widgets to draw themselves.
        """
        painter = QPainter(self)
        if self.display_mode == "signal_light" or self.display_mode == "both":
            self.signal_light.draw(painter)
        if self.display_mode == "dvj" or self.display_mode == "both":
            self.dvj.draw(painter)

    def __init__(self, server_code, train_number, display_mode):
        super().__init__()
        self.server_code = server_code
        self.train_number = train_number
        self.display_mode = display_mode # Store the selected display mode
        self.url = f"{trains_url_template}{server_code}"

        # Create instances of our custom display widgets.
        # Adjust positions based on selected mode if desired for better layout
        if display_mode == "signal_light":
            self.signal_light = SignalLight(x=40, y=0)
            self.dvj = DVJ(x=0, y=0) # DVJ still created but not drawn
        elif display_mode == "dvj":
            self.signal_light = SignalLight(x=0, y=0) # SignalLight still created but not drawn
            self.dvj = DVJ(x=0, y=0)
        else: # "both"
            self.signal_light = SignalLight(x=0, y=0)
            self.dvj = DVJ(x=45, y=0)


        # Configure the window properties.
        self.setWindowTitle("EVM-120")
        self.setWindowIcon(QIcon('./images/logo.ico'))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) # No border, always on top.
        self.setAttribute(Qt.WA_TranslucentBackground) # Make the background transparent.

        # Set initial size based on display mode
        if display_mode == "signal_light":
            self.setGeometry(100, 100, 120, 150)
        elif display_mode == "dvj":
            self.setGeometry(100, 100, 150, 90)
        else: # "both"
            self.setGeometry(100, 100, 200, 150)


        # Set up a timer to fetch data periodically.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_api_data) # Call fetch_api_data every time the timer fires.
        self.timer.start(5000)  # Timer fires every 5000 milliseconds (5 seconds).

        self.old_pos = None # Used to handle window dragging.

    def fetch_api_data(self):
        """
        Called by the timer to fetch data from the API, process it,
        and trigger a visual update.
        """
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                data = response.json()
                train_found = False
                # Find our selected train in the list of all trains on the server.
                for train in data.get("data", []):
                    if train.get("TrainNoLocal") == self.train_number:
                        train_data = train.get("TrainData", {})
                        # Get the speed of the signal in front of the train.
                        speed = train_data.get("SignalInFrontSpeed", 0)
                        print(f"Signal Reading: {speed}")
                        # Call the central method to update the visuals.
                        self.update_visuals(speed)
                        train_found = True
                        break
                # If the train is not found (e.g., left the game), reset visuals.
                if not train_found:
                    self.update_visuals(None)
            else:
                self.update_visuals(None) # Reset visuals on API error
        except Exception as e:
            # If any error occurs during the request, reset visuals.
            print(f"Exception occurred during API request: {str(e)}")
            self.update_visuals(None)

    def update_visuals(self, speed):
        """
        This central method updates the state of all visual components based on the speed
        and then schedules a repaint of the window.
        """
        # --- Update the state of the DVJ (digital display) ---
        if self.display_mode == "dvj" or self.display_mode == "both":
            speed = 100
            if speed is None:
                self.dvj.set_speed("ERR")  # Show "ERR" if there's no data or an error.
            elif speed == 32767:
                self.dvj.set_speed("MAX")  # Show "MAX" for this specific high-speed value.
            elif speed == 0:
                self.dvj.set_speed(" o ")  # Show "MAX" for this specific high-speed value.
            elif speed >= 100:
                self.dvj.set_speed(speed)
            else:
                self.dvj.set_speed(f" {speed}")  # For all other cases, show the actual speed number.

        # --- Update the state of the SignalLight ---
        if self.display_mode == "signal_light" or self.display_mode == "both":
            if speed == 0:
                self.signal_light.set_aspect(2)  # Red light.
            elif speed in [40, 60]:
                self.signal_light.set_aspect(1, 3)  # Double orange.
            elif speed in [80, 100]:
                self.signal_light.set_aspect(0, 3)  # Green and orange.
            elif speed is not None and speed > 100:
                self.signal_light.set_aspect(0)  # Green light.
            else:
                self.signal_light.set_aspect() # All lights off (default/error state).
        
        # Optionally, send the final displayed text to the Arduino.
        # sendMessage(self.dvj.label_text)

        # --- Schedule a Repaint ---
        # This is crucial. It tells PyQt that the widget's state has changed
        # and it needs to be redrawn, which will trigger the paintEvent.
        self.update()

    # --- WINDOW MOVEMENT AND CLOSE EVENTS ---
    def mousePressEvent(self, event):
        """Captures the mouse position when the left button is pressed."""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.pos()

    def mouseMoveEvent(self, event):
        """Moves the window based on how much the mouse has moved."""
        if self.old_pos is not None:
            delta = event.pos() - self.old_pos
            self.move(self.pos() + delta)

    def mouseReleaseEvent(self, event):
        """Resets the stored mouse position when the left button is released."""
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def keyPressEvent(self, event):
        """Closes the application if the Escape key is pressed."""
        if event.key() == Qt.Key_Escape:
            self.close()


# --- APPLICATION ENTRY POINT ---
if __name__ == "__main__":
    # This block runs only when the script is executed directly.
    app = QApplication(sys.argv)
    
    # Create and show the startup dialog first.
    startup_dialog = StartupDialog()
    print("Starting Application...")
    
    # The '.exec_()' shows the dialog and waits until it is closed.
    if startup_dialog.exec_() == QDialog.Accepted:
        # This code runs only if the user clicks "Start" with valid selections.
        print(f"Selected: Server {startup_dialog.server_code}, Train {startup_dialog.train_number}, Display Mode: {startup_dialog.display_mode}")
        server_code = startup_dialog.server_code
        train_number = startup_dialog.train_number
        display_mode = startup_dialog.display_mode

        # Create and show the main transparent window.
        transparent_window = TransparentWindow(server_code, train_number, display_mode)
        # The initial geometry is now set inside TransparentWindow's __init__
        transparent_window.show()

        # Start the application's main event loop and exit when it's done.
        sys.exit(app.exec_())