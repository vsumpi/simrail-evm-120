import pytest
from PyQt5.QtWidgets import QApplication, QMessageBox
from main import StartupDialog, TransparentWindow  # Import your classes
from PyQt5.QtGui import QPixmap

@pytest.fixture(scope='module')
def app():
    return QApplication([])

@pytest.fixture
def startup_dialog(qtbot):
    dialog = StartupDialog()
    qtbot.addWidget(dialog)
    return dialog

@pytest.fixture
def transparent_window(qtbot):
    window = TransparentWindow("server_code", "train_number")
    qtbot.addWidget(window)
    return window

# Test if the dropdowns get populated
@pytest.mark.parametrize("dropdown", ["server_combo", "train_combo"])
def test_dropdown_filled(startup_dialog, dropdown):
    print(f"Executing test: test_dropdown_filled for {dropdown}")
    combo_box = getattr(startup_dialog, dropdown)
    if combo_box.count() == 0:
        print(f"WARNING: {dropdown} is empty after fetching data")
    assert combo_box.count() > 0, f"{dropdown} should be populated after fetching data"
    print("Status: PASSED")

# Test if the window starts after clicking "Start"
def test_start_application(qtbot, startup_dialog):
    print("Executing test: test_start_application")
    startup_dialog.start_button.click()
    if startup_dialog.isVisible():
        print("ERROR: StartupDialog did not close after clicking Start")
    assert startup_dialog.isVisible() is False, "StartupDialog should close after clicking Start"
    print("Status: PASSED")

# Test if images load correctly
def test_image_loading(transparent_window):
    print("Executing test: test_image_loading")
    test_images = ["speed_0.gif", "speed_40.gif", "speed_80.gif", "speed_high.gif"]
    for image in test_images:
        transparent_window.load_image(image)
        if transparent_window.image_label.pixmap().isNull():
            print(f"ERROR: Image {image} failed to load")
            assert False, f"Image {image} should be loaded correctly"
        else:
            print(f"Status: PASSED for {image}")

# Test if all windows have correct title
def test_window_title(startup_dialog, transparent_window):
    print("Executing test: test_window_title")
    if startup_dialog.windowTitle() != "EVM120":
        print("WARNING: StartupDialog title is incorrect")
    if transparent_window.windowTitle() != "EVM120":
        print("WARNING: TransparentWindow title is incorrect")
    assert startup_dialog.windowTitle() == "EVM120", "StartupDialog title should be 'EVM120'"
    assert transparent_window.windowTitle() == "EVM120", "TransparentWindow title should be 'EVM120'"
    print("Status: PASSED")

# Test for failed Qt elements (basic element existence check)
def test_qt_elements_exist(startup_dialog):
    print("Executing test: test_qt_elements_exist")
    if startup_dialog.server_combo is None:
        print("ERROR: Server dropdown is missing")
    if startup_dialog.train_combo is None:
        print("ERROR: Train dropdown is missing")
    if startup_dialog.start_button is None:
        print("ERROR: Start button is missing")
    assert startup_dialog.server_combo is not None, "Server dropdown should exist"
    assert startup_dialog.train_combo is not None, "Train dropdown should exist"
    assert startup_dialog.start_button is not None, "Start button should exist"
    print("Status: PASSED")
