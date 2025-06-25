#!/usr/bin/env python3
# Standard library imports
import os
import json
import base64
import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Third-party imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class PontoApp(Gtk.Application):
    def __init__(self, auto_trigger=False):
        super().__init__(application_id="com.icarus.pontoapp")
        self.connect("activate", self.on_activate)
        self.auto_trigger = auto_trigger
        
        # Configuration
        self.config_dir = os.path.join(str(Path.home()), ".config", "ponto_app")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.username = ""
        self.encrypted_password = ""
        self.secret_key = "Dyn@"
        self.salt = b'pontoapp_salt_123'  # Fixed salt for key derivation
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load configuration if exists
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.username = config.get('username', '')
                    self.encrypted_password = config.get('encrypted_password', '')
            except Exception as e:
                self.show_error_dialog("Configuration Error", f"Error loading configuration: {e}")

    def save_config(self):
        config = {
            'username': self.username,
            'encrypted_password': self.encrypted_password
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            # Set proper permissions to protect the password
            os.chmod(self.config_file, 0o600)
        except Exception as e:
            self.show_error_dialog("Configuration Error", f"Error saving configuration: {e}")

    def on_activate(self, app):
        # Create the main window
        self.window = Gtk.ApplicationWindow(application=app, title="Ponto App")
        self.window.set_default_size(400, 300)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        
        # Create a header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("Ponto App")
        self.window.set_titlebar(header)
        
        # Settings button
        settings_button = Gtk.Button()
        settings_button.set_tooltip_text("Configurações")
        settings_icon = Gtk.Image.new_from_icon_name("preferences-system-symbolic", Gtk.IconSize.BUTTON)
        settings_button.add(settings_icon)
        settings_button.connect("clicked", self.on_settings_clicked)
        header.pack_end(settings_button)
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        self.window.add(main_box)
        
        # Current time label
        self.time_label = Gtk.Label()
        self.update_time()
        main_box.pack_start(self.time_label, False, False, 0)
        
        # Update time every second
        GLib.timeout_add_seconds(1, self.update_time)
        
        # Button to clock in/out
        self.clock_button = Gtk.Button(label="Bater Ponto")
        self.clock_button.connect("clicked", self.on_clock_button_clicked)
        self.clock_button.set_size_request(-1, 50)
        main_box.pack_start(self.clock_button, False, False, 10)
        
        # Status label
        self.status_label = Gtk.Label(label="")
        main_box.pack_start(self.status_label, False, False, 0)
        
        # Show all widgets
        self.window.show_all()
        
        # Check if we need to show settings on first run
        if not self.username or not self.encrypted_password:
            self.show_settings_dialog()
        
        # If auto_trigger is enabled, automatically click the clock button
        if self.auto_trigger and self.username and self.encrypted_password:
            # Add a short delay to ensure UI is fully loaded
            GLib.timeout_add(500, self.trigger_clock_button)

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%d/%m/%Y")
        self.time_label.set_text(f"{current_date} - {current_time}")
        return True

    def on_clock_button_clicked(self, button):
        if not self.username or not self.encrypted_password:
            self.show_error_dialog("Configurações incompletas", "Por favor, configure seu usuário e senha nas configurações.")
            self.show_settings_dialog()
            return
        
        # Ask for confirmation
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Você deseja bater o ponto agora?"
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            self.register_time()
    
    def register_time(self):
        try:
            # Get decrypted password using cryptography library
            password = self.decrypt_password()
            if not password:
                self.show_error_dialog("Erro", "Não foi possível descriptografar a senha.")
                return
            
            # API endpoints
            login_url = "https://backendicarus.pontoicarus.com.br/usuario/logar"
            register_url = "https://backendicarus.pontoicarus.com.br/ponto/bater"
            
            # Login and get token
            login_data = {
                "username": self.username,
                "password": password
            }
            
            self.status_label.set_text("Autenticando...")
            self.window.queue_draw()
            
            response = requests.post(login_url, json=login_data)
            response.raise_for_status()
            auth_data = response.json()
            
            token = auth_data.get('token')
            if not token:
                self.show_error_dialog("Erro de autenticação", "Falha ao obter token de autenticação.")
                return
            
            id_mutuario = auth_data.get('employee', [{}])[0].get('idMutuario')
            if not id_mutuario:
                self.show_error_dialog("Erro", "Falha ao obter idMutuario.")
                return
            
            # Data to send for clock in/out
            register_data = {
                "idMutuario": id_mutuario,
                "latitude": -27.572293,
                "longitude": -48.5095271,
                "precisao": 42.5,
                "meioBatida": "NAVEGADOR"
            }
            
            self.status_label.set_text("Registrando ponto...")
            self.window.queue_draw()
            
            # Send authenticated request
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            # print headers and register_data for debugging
            print("Headers:", headers)
            print("Register Data:", register_data)  
            
            
            response = requests.post(register_url, json=register_data, headers=headers)
            #response.raise_for_status() # Get 400 with message when error, and the message is important
            result = response.json()

            message = result.get('message', 'Sem mensagem do servidor')
            current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            full_message = f"{current_datetime}\n{message}"
            
            self.show_info_dialog("Registro de Ponto", full_message)
            self.status_label.set_text(message)
            
        except requests.exceptions.RequestException as e:
            self.show_error_dialog("Erro", f"Ocorreu um erro de rede: {e}")
            self.status_label.set_text(f"Erro: {e}")
        except Exception as e:
            self.show_error_dialog("Erro", f"Ocorreu um erro: {e}")
            self.status_label.set_text(f"Erro: {e}")

    
    def encrypt_password(self, password):
        try:
            # Generate a key from the secret_key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
            
            # Create a Fernet instance with the derived key
            fernet = Fernet(key)
            
            # Encrypt the password
            encrypted_bytes = fernet.encrypt(password.encode())
            
            # Store the encrypted password as a base64 string
            self.encrypted_password = encrypted_bytes.decode()
            
        except Exception as e:
            self.show_error_dialog("Encryption Error", f"Failed to encrypt password: {e}")
    
    def decrypt_password(self):
        try:
            if not self.encrypted_password:
                return None
                
            # Generate the same key from the secret_key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
            
            # Create a Fernet instance with the derived key
            fernet = Fernet(key)
            
            # Decrypt the password
            decrypted_bytes = fernet.decrypt(self.encrypted_password.encode())
            decrypted_password = decrypted_bytes.decode()
            
            return decrypted_password
            
        except Exception as e:
            self.show_error_dialog("Decryption Error", f"Failed to decrypt password: {e}")
            return None
    
    def on_settings_clicked(self, button):
        self.show_settings_dialog()
    
    def show_settings_dialog(self):
        dialog = Gtk.Dialog(
            title="Configurações",
            transient_for=self.window,
            flags=0
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        dialog.set_default_size(350, 200)
        
        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        # Username field
        username_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        username_label = Gtk.Label(label="Usuário:")
        username_box.pack_start(username_label, False, False, 0)
        
        username_entry = Gtk.Entry()
        username_entry.set_text(self.username)
        username_box.pack_start(username_entry, True, True, 0)
        box.add(username_box)
        
        # Password field
        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        password_label = Gtk.Label(label="Senha:")
        password_box.pack_start(password_label, False, False, 0)
        
        password_entry = Gtk.Entry()
        password_entry.set_visibility(False)
        password_entry.set_placeholder_text("Digite sua senha")
        password_box.pack_start(password_entry, True, True, 0)
        box.add(password_box)
        
        # Show all widgets
        dialog.show_all()
        
        # Run the dialog
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            new_username = username_entry.get_text()
            new_password = password_entry.get_text()
            
            self.username = new_username
            
            # Only encrypt password if it was changed
            if new_password:
                self.encrypt_password(new_password)
            
            self.save_config()
        
        dialog.destroy()
    
    def show_error_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def show_info_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def trigger_clock_button(self):
        """Automatically trigger the clock button click"""
        if self.clock_button:
            self.clock_button.clicked()
        return False  # Don't repeat this timeout

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Ponto App - Aplicativo para registro de ponto')
    parser.add_argument('--auto', action='store_true', help='Iniciar com diálogo de confirmação de ponto')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    app = PontoApp(auto_trigger=args.auto)
    app.run()
