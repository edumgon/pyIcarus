#!/usr/bin/env python3
# Standard library imports
import os
import json
import base64
from pathlib import Path
from datetime import datetime

# Third-party imports
import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import geocoder

def get_current_location():
    g = geocoder.ip('me')
    if g.ok:
        return g.lat, g.lng
    return None, None


class PontoBackend:
    """Backend class for Ponto App that handles configuration and API interactions."""
    
    def __init__(self):
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
        """Load username and encrypted password from config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.username = config.get('username', '')
                    self.encrypted_password = config.get('encrypted_password', '')
                return True
            except Exception as e:
                return False, f"Error loading configuration: {e}"
        return True

    def save_config(self):
        """Save username and encrypted password to config file."""
        config = {
            'username': self.username,
            'encrypted_password': self.encrypted_password
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            # Set proper permissions to protect the password
            os.chmod(self.config_file, 0o600)
            return True, "Configuration saved successfully"
        except Exception as e:
            return False, f"Error saving configuration: {e}"

    def encrypt_password(self, password):
        """Encrypt the password using Fernet symmetric encryption."""
        try:
            # Generate a key from the secret key and salt
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
            self.encrypted_password = encrypted_bytes.decode()
            return True, "Password encrypted successfully"
            
        except Exception as e:
            return False, f"Failed to encrypt password: {e}"

    def decrypt_password(self):
        """Decrypt the stored password."""
        try:
            if not self.encrypted_password:
                return False, "No password stored"
                
            # Generate a key from the secret key and salt
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
            
            return True, decrypted_password
            
        except Exception as e:
            return False, f"Failed to decrypt password: {e}"

    def register_time(self):
        """Register time with the API."""
        try:
            # Get current time
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            
            # Get password
            success, password_result = self.decrypt_password()
            if not success:
                return False, password_result, current_time
            
            password = password_result
            
            # API endpoints - using the correct endpoints from the original app
            login_url = "https://backendicarus.pontoicarus.com.br/usuario/logar"
            register_url = "https://backendicarus.pontoicarus.com.br/ponto/bater"
            
            # Login and get token
            login_data = {
                "username": self.username,
                "password": password
            }
            
            # Make login API request
            login_response = requests.post(login_url, json=login_data)
            
            if login_response.status_code != 200:
                return False, f"Falha na autenticação: {login_response.status_code}", current_time
            
            # Check if response has content before parsing JSON
            if not login_response.text.strip():
                return False, "Resposta de autenticação vazia", current_time
                
            try:
                auth_data = login_response.json()
            except ValueError as json_err:
                return False, f"Erro ao processar resposta de autenticação: {json_err}", current_time
            
            token = auth_data.get('token')
            
            if not token:
                return False, "Falha ao obter token de autenticação", current_time
            
            id_mutuario = auth_data.get('employee', [{}])[0].get('idMutuario')
            if not id_mutuario:
                return False, "Falha ao obter idMutuario", current_time

            # Get real location
            latitude, longitude = get_current_location()  # or get_location()

            # Fallback to default values if location couldn't be determined
            if latitude is None or longitude is None:
                latitude, longitude = -27.572293, -48.5095271  # Keep your current defaults

            register_data = {
                "idMutuario": id_mutuario,
                "latitude": latitude,
                "longitude": longitude,
                "precisao": 42.5,  # You might want to get real accuracy too
                "meioBatida": "NAVEGADOR"
            }

            # Data to send for clock in/out
#            register_data = {
#                "idMutuario": id_mutuario,
#                "latitude": -27.572293,
#                "longitude": -48.5095271,
#                "precisao": 42.5,
#                "meioBatida": "NAVEGADOR"
#            }
            
            # Send authenticated request
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=UTF-8"
            }
            
            # Make register time API request
            register_response = requests.post(register_url, json=register_data, headers=headers)
            
            # Handle successful response codes
            if register_response.status_code == 200 or register_response.status_code == 201:
                # Check if response is plain text "ok"
                if register_response.text.strip().lower() == "ok":
                    return True, "Ponto registrado com sucesso", current_time
                    
                # Try to parse as JSON if not plain "ok"
                try:
                    result = register_response.json()
                    message = result.get('message', 'Ponto registrado com sucesso')
                    return True, message, current_time
                except ValueError:
                    # If can't parse as JSON but status code is success, consider it successful
                    return True, "Ponto registrado com sucesso", current_time
            else:
                # Handle error responses
                try:
                    result = register_response.json()
                    message = result.get('message', 'Erro ao registrar ponto')
                except ValueError:
                    # If can't parse error as JSON, use response text or status code
                    message = register_response.text.strip() if register_response.text.strip() else f"Erro {register_response.status_code}"
                
                return False, message, current_time
        
        except Exception as e:
            return False, f"Falha ao registrar ponto: {e}", datetime.now().strftime("%H:%M:%S")

    def update_credentials(self, username, password=None):
        """Update username and password."""
        self.username = username
        
        if password:
            success, message = self.encrypt_password(password)
            if not success:
                return False, message
        
        success, message = self.save_config()
        return success, message
