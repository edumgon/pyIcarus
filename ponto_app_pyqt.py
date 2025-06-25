#!/usr/bin/env python3
# Standard library imports
import sys
import argparse
from datetime import datetime

# Third-party imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QDialog, QLineEdit, QMessageBox, 
    QDialogButtonBox, QFormLayout
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon

# Local imports
from ponto_backend import PontoBackend


class SettingsDialog(QDialog):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.resize(350, 200)
        
        # Create form layout
        layout = QFormLayout(self)
        
        # Username field
        self.username_entry = QLineEdit()
        self.username_entry.setText(username)
        layout.addRow("Usuário:", self.username_entry)
        
        # Password field
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_entry.setPlaceholderText("Digite sua senha")
        layout.addRow("Senha:", self.password_entry)
        
        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)


class PontoAppPyQt(QMainWindow):
    def __init__(self, auto_trigger=False):
        super().__init__()
        self.auto_trigger = auto_trigger
        
        # Initialize backend
        self.backend = PontoBackend()
        
        # Setup UI
        self.init_ui()
        
        # Trigger clock button if auto_trigger is True
        if self.auto_trigger:
            QTimer.singleShot(500, self.trigger_clock_button)

    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Ponto App")
        self.resize(400, 300)
        self.setWindowIcon(QIcon.fromTheme("clock"))
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        
        # Settings button in toolbar
        toolbar = self.addToolBar("Settings")
        settings_action = toolbar.addAction("Settings")
        settings_action.setIcon(QIcon.fromTheme("preferences-system"))
        settings_action.triggered.connect(self.on_settings_clicked)
        
        # Current time label
        self.time_label = QLabel()
        self.update_time()
        main_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Update time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        # Button to clock in/out
        self.clock_button = QPushButton("Bater Ponto")
        self.clock_button.setMinimumHeight(50)
        self.clock_button.clicked.connect(self.on_clock_button_clicked)
        main_layout.addWidget(self.clock_button)
        
        # Status label
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Show the window
        self.show()

    def update_time(self):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d/%m/%Y")
        self.time_label.setText(f"<h2>{time_str}</h2><p>{date_str}</p>")
        return True

    def on_clock_button_clicked(self):
        if not self.backend.username or not self.backend.encrypted_password:
            self.show_error_dialog("Configuração Necessária", 
                                  "Por favor, configure seu usuário e senha primeiro.")
            self.on_settings_clicked()
            return
        
        # Ask for confirmation before registering time
        confirm_response = QMessageBox.question(
            self, 
            "Confirmação",
            "Bater ponto agora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        # If user doesn't confirm, return without registering time
        if confirm_response != QMessageBox.StandardButton.Yes:
            return
        
        self.status_label.setText("Registrando ponto...")
        QApplication.processEvents()
        
        # Register time using backend
        success, message, current_time = self.backend.register_time()
        
        if success:
            self.show_info_dialog("Sucesso", message)
            self.status_label.setText(f"Último registro: {current_time}")
        else:
            self.show_error_dialog("Erro", message)
            self.status_label.setText("Falha ao registrar ponto.")

    def on_settings_clicked(self):
        dialog = SettingsDialog(self, self.backend.username)
        if dialog.exec():
            new_username = dialog.username_entry.text()
            new_password = dialog.password_entry.text()
            
            # Update credentials using backend
            success, message = self.backend.update_credentials(new_username, new_password if new_password else None)
            
            self.status_label.setText(message)

    def show_error_dialog(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_info_dialog(self, title, message):
        QMessageBox.information(self, title, message)

    def trigger_clock_button(self):
        """Automatically trigger the clock button click"""
        if self.clock_button:
            self.clock_button.click()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Ponto App - Aplicativo para registro de ponto')
    parser.add_argument('--auto', action='store_true', help='Iniciar com diálogo de confirmação de ponto')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    app = QApplication(sys.argv)
    window = PontoAppPyQt(auto_trigger=args.auto)
    sys.exit(app.exec())
