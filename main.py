import sys
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QSlider, QLabel, QWidget, QGroupBox,
                             QMessageBox)
from PyQt5.QtCore import Qt
import pymem
import pymem.process

class CS2Controller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pm = None
        self.client = None
        self.dwLocalPlayerController = None
        self.dwLocalPlayerPawn = None
        self.is_injected = False
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Akw Cheat BETA")
        self.setFixedSize(400, 500)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Inject button
        self.inject_btn = QPushButton("INJECT")
        self.inject_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #cc3333;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)
        self.inject_btn.clicked.connect(self.toggle_injection)
        layout.addWidget(self.inject_btn)
        
        # Status label
        self.status_label = QLabel("Status: Not injected")
        self.status_label.setStyleSheet("font-weight: bold; color: #ff4444;")
        layout.addWidget(self.status_label)
        
        # FOV Control Group
        fov_group = QGroupBox("Field of View Control")
        fov_layout = QVBoxLayout(fov_group)
        
        # FOV slider and value display
        fov_control_layout = QHBoxLayout()
        fov_control_layout.addWidget(QLabel("FOV:"))
        
        self.fov_value_label = QLabel("120")
        self.fov_value_label.setFixedWidth(30)
        fov_control_layout.addWidget(self.fov_value_label)
        fov_control_layout.addStretch()
        
        fov_layout.addLayout(fov_control_layout)
        
        self.fov_slider = QSlider(Qt.Horizontal)
        self.fov_slider.setRange(60, 160)
        self.fov_slider.setValue(120)
        self.fov_slider.valueChanged.connect(self.update_fov_value)
        self.fov_slider.sliderReleased.connect(self.apply_fov)
        fov_layout.addWidget(self.fov_slider)
        
        # FOV apply button
        self.fov_apply_btn = QPushButton("Apply FOV")
        self.fov_apply_btn.clicked.connect(self.apply_fov)
        self.fov_apply_btn.setEnabled(False)
        fov_layout.addWidget(self.fov_apply_btn)
        
        layout.addWidget(fov_group)
        
        # Feature Buttons Group
        features_group = QGroupBox("Features")
        features_layout = QVBoxLayout(features_group)
        
        # Remove Recoil button
        self.recoil_btn = QPushButton("Remove Recoil")
        self.recoil_btn.setStyleSheet("""
            QPushButton {
                background-color: #4444ff;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3333cc;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)
        self.recoil_btn.clicked.connect(self.remove_recoil)
        self.recoil_btn.setEnabled(False)
        features_layout.addWidget(self.recoil_btn)
        
        # Flashbang Duration button
        self.flashbang_btn = QPushButton("Remove Flashbang Duration")
        self.flashbang_btn.setStyleSheet("""
            QPushButton {
                background-color: #44ff44;
                color: black;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #33cc33;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)
        self.flashbang_btn.clicked.connect(self.remove_flashbang_duration)
        self.flashbang_btn.setEnabled(False)
        features_layout.addWidget(self.flashbang_btn)
        
        layout.addWidget(features_group)
        
        # Add some spacing at the bottom
        layout.addStretch()
        
    def update_fov_value(self, value):
        self.fov_value_label.setText(str(value))
        
    def toggle_injection(self):
        if not self.is_injected:
            self.inject()
        else:
            self.eject()
            
    def inject(self):
        try:
            # Run injection in a separate thread to prevent UI freezing
            thread = threading.Thread(target=self._inject_thread)
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.show_error(f"Injection failed: {str(e)}")
            
    def _inject_thread(self):
        try:
            # Update UI from thread
            self.inject_btn.setEnabled(False)
            self.inject_btn.setText("INJECTING...")
            self.status_label.setText("Status: Injecting...")
            
            # Perform injection
            self.pm = pymem.Pymem("cs2.exe")
            self.client = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
            
            # Read addresses
            self.dwLocalPlayerController = self.pm.read_longlong(self.client.lpBaseOfDll + 0x1E16870)
            self.dwLocalPlayerPawn = self.pm.read_longlong(self.client.lpBaseOfDll + 0x1BE7DA0)
            
            # Update UI on success
            self.is_injected = True
            self.inject_btn.setText("EJECT")
            self.inject_btn.setEnabled(True)
            self.status_label.setText("Status: Injected ✓")
            self.status_label.setStyleSheet("font-weight: bold; color: #44ff44;")
            
            # Enable controls
            self.fov_apply_btn.setEnabled(True)
            self.recoil_btn.setEnabled(True)
            self.flashbang_btn.setEnabled(True)
            
        except Exception as e:
            # Update UI on error
            self.inject_btn.setText("INJECT")
            self.inject_btn.setEnabled(True)
            self.status_label.setText("Status: Injection failed")
            self.show_error(f"Injection failed: {str(e)}")
            
    def eject(self):
        try:
            self.pm.close_process()
            self.is_injected = False
            self.inject_btn.setText("INJECT")
            self.status_label.setText("Status: Not injected")
            self.status_label.setStyleSheet("font-weight: bold; color: #ff4444;")
            
            # Disable controls
            self.fov_apply_btn.setEnabled(False)
            self.recoil_btn.setEnabled(False)
            self.flashbang_btn.setEnabled(False)
            
        except Exception as e:
            self.show_error(f"Ejection failed: {str(e)}")
            
    def apply_fov(self):
        if not self.is_injected:
            self.show_error("Not injected into CS2!")
            return
            
        try:
            fov_value = self.fov_slider.value()
            self.pm.write_int(self.dwLocalPlayerController + 0x77C, fov_value)
            self.show_info(f"FOV set to {fov_value}")
        except Exception as e:
            self.show_error(f"Failed to set FOV: {str(e)}")
            
    def remove_recoil(self):
        if not self.is_injected:
            self.show_error("Not injected into CS2!")
            return
            
        try:
            self.pm.write_float(self.dwLocalPlayerPawn + 0x1A08, 0.0)
            self.show_info("Recoil removed")
        except Exception as e:
            self.show_error(f"Failed to remove recoil: {str(e)}")
            
    def remove_flashbang_duration(self):
        if not self.is_injected:
            self.show_error("Not injected into CS2!")
            return
            
        try:
            self.pm.write_float(self.dwLocalPlayerPawn + 0x160C, 50.0)
            self.show_info("Flashbang duration removed")
        except Exception as e:
            self.show_error(f"Failed to remove flashbang duration: {str(e)}")
            
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        
    def show_info(self, message):
        QMessageBox.information(self, "Success", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CS2Controller()
    window.show()
    sys.exit(app.exec_())
