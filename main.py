import sys
from PyQt5.QtWidgets import QApplication

from telemetry import TelemetryClient
#from signal_logic import EVMDecoder
#from gui import MainWindow
#from signal_render import EVMRenderer

def main():
    app = QApplication(sys.argv)

# --- LOAD MODULES ---
    telemetry = TelemetryClient()

    telemetry.block_speed.connect(lambda speed: print(f"Block Speed: {speed}"))
    telemetry.next_block_speed.connect(lambda speed: print(f"Next Block: {speed}"))
    telemetry.error_occurred.connect(lambda err: print(f"ERROR: {err}"))

# --- CONNECTION ---
    telemetry.start()

# --- RUN APP ---
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()