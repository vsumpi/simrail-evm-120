import sys
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,  # Manages the GUI application's control flow and main settings.
    QWidget,  # Base class for all user interface objects.
    QVBoxLayout,  # A layout manager that arranges widgets vertically.
    QLabel,  # A widget for displaying text or images.
    QDialog,  # A base class for dialog windows.
    QPushButton,  # A command button widget.
    QComboBox,  # A dropdown list widget.
    QFormLayout,  # A layout manager for two-column forms (e.g., "Label: [Widget]").
    QMessageBox,  # A dialog for showing messages (warnings, errors, info).
    QTextEdit,
    QDesktopWidget
)
from PyQt5.QtGui import QPainter, QBrush, QFont, QColor, QIcon  # Classes for drawing.
from PyQt5.QtCore import Qt, QTimer  # Core Qt functionalities, including the timer.

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EVM-120 SR Emulator")
        self.setFixedSize(400,250)

        #self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        
        self.layout = QFormLayout(self.centralWidget)

        self.w_main()
    
    def w_main(self):
        self.clear_layout(self.layout)

        self.l_title = QLabel("EVM-120\nSimRail Emulator")
        self.l_title.setStyleSheet("font-size: 32px")
        self.c_server = QComboBox()
        self.c_train = QComboBox()
        self.c_display = QComboBox()
        self.b_start = QPushButton("Start")
        self.b_about = QPushButton("About")
        self.b_about.clicked.connect(self.w_about)

        self.c_server.addItem("HU1")
        self.c_train.addItem("RegioJet")
        self.c_display.addItem("EVM")

        self.layout.addWidget(self.l_title)
        self.layout.addRow("Select Server:", self.c_server)
        self.layout.addRow("Select Train:", self.c_train)
        self.layout.addRow("Display Mode:", self.c_display)
        self.layout.addRow(self.b_about)
        self.layout.addRow(self.b_start)

        self.show()

    def w_about(self):
        self.clear_layout(self.layout)
        
        self.setWindowTitle("EVM-120 SR Emulator")
        self.setFixedSize(400,250)
        
        self.note = QTextEdit(self)
        self.note.setText("Disclaimer: This program is an independent project and is not affiliated with, authorized, maintained, sponsored, or endorsed by SimRail or any of its affiliates or subsidiaries.\nAll product and company names are the registered trademarks of their original owners. The use of any trade name or trademark is for identification and reference purposes only and does not imply any association with the trademark holder of their product brand.")
        self.note.setReadOnly(True)
        self.b_back = QPushButton("Back")
        self.b_back.clicked.connect(self.w_main)

        self.layout.addWidget(self.note)
        self.layout.addWidget(self.b_back)
        self.show()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

app = QApplication(sys.argv)
ow = SettingsWindow()
sys.exit(app.exec_())