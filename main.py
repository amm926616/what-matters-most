from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QSystemTrayIcon, QMenu, QInputDialog, QColorDialog, QDialog, QVBoxLayout, QSlider, QPushButton
from PyQt6.QtGui import QFont, QIcon, QAction, QGuiApplication, QFontDatabase
from PyQt6.QtCore import Qt
import sys
import os
import json
from create_desktop_file import create_desktop_file

def get_config_path():
    """Ensure the config file's directory exists and return its path."""
    config_folder = os.getenv("APPDATA") if os.name == "nt" else os.path.join(os.path.expanduser("~"), '.config')
    config_directory = os.path.join(config_folder, "Focus-F*cker")
    os.makedirs(config_directory, exist_ok=True)
    return config_directory

def get_config_file(config_folder):
    """Ensure the config file exists and return its path."""
    config_file = os.path.join(config_folder, "config.json")
    if not os.path.exists(config_file):
        default_config = {
            'font_color': [100, 255, 255],
            'transparency': 150,
            'reminder_text': "FocusF*cker!"
        }
        try:
            with open(config_file, 'w') as f:
                json.dump(default_config, f)
        except IOError as e:
            print(f"Error writing to config file: {e}")
    return config_file

def load_config():
    """Load configuration and reminder text."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config, config.get('reminder_text', "FocusF*cker!")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading configuration: {e}")
        return {}, "FocusF*cker!"

# Paths and Config Initialization
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = get_config_path()
CONFIG_FILE = get_config_file(CONFIG_PATH)
ICON_PATH = os.path.join(SCRIPT_PATH, 'icon.png')
EXE_PATH = os.path.join(SCRIPT_PATH, 'main.py')
CONFIGS, PREVIOUS_TEXT = load_config()

class TransparentReminder(QWidget):
    def __init__(self, text, desktop_app_file):
        super().__init__()

        self.font_color = CONFIGS.get('font_color', [255, 0, 0])
        self.transparency = CONFIGS.get('transparency', 150)

        QGuiApplication.setDesktopFileName(desktop_app_file)

        self.custom_font = self.load_custom_font()
        self.label = QLabel(text, self)
        self.label.setStyleSheet(f"color: rgba({self.font_color[0]}, {self.font_color[1]}, {self.font_color[2]}, {self.transparency}); background: transparent;")
        self.label.setFont(self.custom_font)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.position_text(text)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowTransparentForInput)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.adjustSize()
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move((screen_geometry.width() - self.width()) // 2, (screen_geometry.height() - self.height()) // 2)

        self.tray_icon = QSystemTrayIcon(QIcon(ICON_PATH), self)
        self.tray_menu = TrayMenuCustom(self.tray_icon, self.update_text, self.quit_app, self.open_config_window)

    def show_window(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

    def update_text(self):
        new_text, ok = QInputDialog.getText(self, "Update Reminder", "Enter new text:")
        if ok and new_text.strip():
            self.position_text(new_text)
            self.save_text(new_text)

    def save_text(self, new_text):
        """Save the new text to the configuration file."""
        try:
            config, _ = load_config()
            config['reminder_text'] = new_text
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except IOError as e:
            print(f"Error saving reminder text: {e}")

    def position_text(self, new_text):
        self.label.setText(new_text.strip())
        self.label.adjustSize()
        self.adjustSize()
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move((screen_geometry.width() - self.width()) // 2, (screen_geometry.height() - self.height()) // 2)

    def load_custom_font(self):
        font_path = os.path.join(SCRIPT_PATH, "fonts", "KOMIKAX_.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("Custom font not found, using default font.")
            return QFont("Arial", 24)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        return QFont(font_family, 24)

    def open_config_window(self):
        self.config_window = ConfigWindow(self.font_color, self.transparency, self.apply_config_changes)
        self.config_window.show()

    def apply_config_changes(self, font_color, transparency):
        self.font_color = font_color
        self.transparency = transparency
        self.label.setStyleSheet(f"color: rgba({self.font_color[0]}, {self.font_color[1]}, {self.font_color[2]}, {self.transparency}); background: transparent;")
        self.save_config()

    def quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()

    def save_config(self):
        """Save current configuration to a JSON file."""
        config = {'font_color': self.font_color, 'transparency': self.transparency}
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except IOError as e:
            print(f"Error saving configuration: {e}")

class TrayMenuCustom:
    def __init__(self, tray_icon, update_text, quit_app, open_config_window):
        self.tray_icon = tray_icon
        self.tray_menu = QMenu()

        self.update_text_action = QAction("Update Text")
        self.quit_action = QAction("Quit")
        self.configurations_action = QAction("Configurations")

        self.update_text_action.triggered.connect(update_text)
        self.quit_action.triggered.connect(quit_app)
        self.configurations_action.triggered.connect(open_config_window)

        self.tray_menu.addAction(self.update_text_action)
        self.tray_menu.addAction(self.configurations_action)
        self.tray_menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.show_window)
        self.tray_icon.show()

    def show_window(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.tray_icon.show()

class ConfigWindow(QDialog):
    def __init__(self, current_font_color, current_transparency, apply_changes_callback):
        super().__init__()
        self.setWindowTitle("Configuration")
        self.apply_changes_callback = apply_changes_callback
        self.font_color = current_font_color
        self.transparency = current_transparency

        self.color_button = QPushButton("Choose Font Color", self)
        self.color_button.clicked.connect(self.choose_color)

        self.transparency_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.transparency_slider.setRange(0, 255)
        self.transparency_slider.setValue(self.transparency)
        self.transparency_slider.setTickInterval(10)
        self.transparency_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.transparency_label = QLabel(f"Transparency: {self.transparency}", self)

        self.transparency_slider.valueChanged.connect(self.update_transparency_label)

        self.apply_button = QPushButton("Apply", self)
        self.apply_button.clicked.connect(self.apply_changes)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.color_button)
        layout.addWidget(self.transparency_slider)
        layout.addWidget(self.transparency_label)
        layout.addWidget(self.apply_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def update_transparency_label(self):
        self.transparency_label.setText(f"Transparency: {self.transparency_slider.value()}")

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.font_color = color.getRgb()[:3]

    def apply_changes(self):
        transparency = self.transparency_slider.value()
        self.apply_changes_callback(self.font_color, transparency)
        self.accept()

def main():
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    desktop_app_file = create_desktop_file(ICON_PATH, EXE_PATH)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    reminder = TransparentReminder(PREVIOUS_TEXT, desktop_app_file)
    reminder.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
