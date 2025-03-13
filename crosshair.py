import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSlider, QColorDialog, QLabel, QCheckBox, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QMouseEvent
import tkinter as tk
import ctypes

class CrosshairOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set window flags for frameless, always-on-top, and transparent interaction
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.BlankCursor)  # Hides the mouse cursor
        root = tk.Tk()
        self.setFixedSize(root.winfo_screenwidth(), root.winfo_screenheight())  # Fullscreen dimensions 
        self.make_window_click_through()  # Ensure window ignores mouse events

        # Default crosshair settings
        self.crosshair_color = QColor(255, 255, 255)  # Default white
        self.line_thickness = 1
        self.line_length = 2
        self.gap_size = 1
        self.middle_dot_enabled = True
        self.middle_dot_size = 1
        self.visible = True # track visability of the crosshair

    def make_window_click_through(self):
        """Makes the overlay window click-through using Windows API."""
        hwnd = self.winId().__int__()  # Get the window handle
        # Get current extended window style
        extended_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE = -20
        # Add WS_EX_LAYERED (transparent) and WS_EX_TRANSPARENT (click-through) styles
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, extended_style | 0x00000020 | 0x00080000)

    def paintEvent(self, event):
        """Draws the crosshair based on the current settings."""
        if not self.visible:
            return
        
        
        painter = QPainter(self)
        pen = QPen(self.crosshair_color, self.line_thickness, Qt.SolidLine)
        painter.setPen(pen)

        center_x, center_y = self.width() // 2, self.height() // 2

        # Draw vertical lines
        painter.drawLine(center_x, center_y - self.gap_size - self.line_length,
                         center_x, center_y - self.gap_size)
        painter.drawLine(center_x, center_y + self.gap_size,
                         center_x, center_y + self.gap_size + self.line_length)

        # Draw horizontal lines
        painter.drawLine(center_x - self.gap_size - self.line_length, center_y,
                         center_x - self.gap_size, center_y)
        painter.drawLine(center_x + self.gap_size, center_y,
                         center_x + self.gap_size + self.line_length, center_y)

        # Draw middle dot
        if self.middle_dot_enabled:
            pen.setWidth(self.middle_dot_size)
            painter.setPen(pen)
            painter.drawPoint(center_x, center_y)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            self.right_click_pressed = True
            self.toggle_visibility()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            self.right_click_pressed = False
            self.visible = True
            self.update()

    def toggle_visibility(self):
        if self.right_click_pressed:
            self.visible = False
            self.update()


class SettingsMenu(QWidget):
    def __init__(self, overlay):
        super().__init__()
        self.overlay = overlay
        self.setWindowTitle("Crosshair Settings")
        self.setFixedSize(200, 300)
        self.initUI()

    def initUI(self):
        """Initializes the settings menu UI."""
        layout = QVBoxLayout()

        # Line Thickness Slider
        layout.addWidget(QLabel("Line Thickness"))
        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setMinimum(1)
        self.thickness_slider.setMaximum(10)
        self.thickness_slider.setValue(self.overlay.line_thickness)
        self.thickness_slider.valueChanged.connect(self.update_thickness)
        layout.addWidget(self.thickness_slider)

        # Line Length Slider
        layout.addWidget(QLabel("Line Length"))
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setMinimum(0)
        self.length_slider.setMaximum(200)
        self.length_slider.setValue(self.overlay.line_length)
        self.length_slider.valueChanged.connect(self.update_length)
        layout.addWidget(self.length_slider)

        # Gap Size Slider
        layout.addWidget(QLabel("Gap Size"))
        self.gap_slider = QSlider(Qt.Horizontal)
        self.gap_slider.setMinimum(0)
        self.gap_slider.setMaximum(50)
        self.gap_slider.setValue(self.overlay.gap_size)
        self.gap_slider.valueChanged.connect(self.update_gap)
        layout.addWidget(self.gap_slider)

        # Middle Dot Toggle
        self.middle_dot_checkbox = QCheckBox("Enable Middle Dot")
        self.middle_dot_checkbox.setChecked(self.overlay.middle_dot_enabled)
        self.middle_dot_checkbox.stateChanged.connect(self.toggle_middle_dot)
        layout.addWidget(self.middle_dot_checkbox)

        # Middle Dot Size Slider
        layout.addWidget(QLabel("Middle Dot Size"))
        self.middle_dot_slider = QSlider(Qt.Horizontal)
        self.middle_dot_slider.setMinimum(1)
        self.middle_dot_slider.setMaximum(20)
        self.middle_dot_slider.setValue(self.overlay.middle_dot_size)
        self.middle_dot_slider.valueChanged.connect(self.update_middle_dot_size)
        layout.addWidget(self.middle_dot_slider)

        # Color Picker
        self.color_button = QPushButton("Pick Crosshair Color")
        self.color_button.clicked.connect(self.pick_color)
        layout.addWidget(self.color_button)

        # Visibility checkbox
        self.visibility_checkbox = QCheckBox("Crosshair visibility on right click")
        self.visibility_checkbox.setChecked(self.overlay.visible)
        self.visibility_checkbox.setEnabled(False)
        layout.addWidget(self.visibility_checkbox)


        # Save Settings Button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def update_thickness(self, value):
        self.overlay.line_thickness = value
        self.overlay.update()

    def update_length(self, value):
        self.overlay.line_length = value
        self.overlay.update()

    def update_gap(self, value):
        self.overlay.gap_size = value
        self.overlay.update()

    def toggle_middle_dot(self, state):
        self.overlay.middle_dot_enabled = bool(state)
        self.overlay.update()

    def update_middle_dot_size(self, value):
        self.overlay.middle_dot_size = value
        self.overlay.update()

    def pick_color(self):
        color = QColorDialog.getColor(initial=self.overlay.crosshair_color, parent=self)
        if color.isValid():
            self.overlay.crosshair_color = color
            self.overlay.update()

    def toggle_visibility(self, state):
        self.overlay.visible = bool(state)
        self.overlay.update()

    def save_settings(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Settings", "", "JSON Files (*.json)", options=options)
        if file_path:
            import json
            settings = {
                "line_thickness": self.overlay.line_thickness,
                "line_length": self.overlay.line_length,
                "gap_size": self.overlay.gap_size,
                "middle_dot_enabled": self.overlay.middle_dot_enabled,
                "middle_dot_size": self.overlay.middle_dot_size,
                "crosshair_color": self.overlay.crosshair_color.name(),
            }
            with open(file_path, 'w') as f:
                json.dump(settings, f)
            print(f"Settings saved to {file_path}")


def main():
    app = QApplication(sys.argv)

    # Create crosshair overlay
    overlay = CrosshairOverlay()
    overlay.show()

    # Create settings menu
    menu = SettingsMenu(overlay)
    menu.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
