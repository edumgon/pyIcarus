#!/usr/bin/env python3
# Standard library imports
import sys
import argparse
from datetime import datetime

# Third-party imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

# Local imports
from ponto_backend import PontoBackend


class PontoAppGTK(Gtk.Application):
    def __init__(self, auto_trigger=False):
        super().__init__(application_id="com.icarus.pontoapp")
        self.connect("activate", self.on_activate)
        self.auto_trigger = auto_trigger
        
        # Initialize backend
        self.backend = PontoBackend()

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
        
        # Automatically trigger the clock button click if requested
        if self.auto_trigger:
            GLib.timeout_add(500, self.trigger_clock_button)

    def update_time(self):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d/%m/%Y")
        self.time_label.set_markup(f"<span size='xx-large'>{time_str}</span>\n<span size='large'>{date_str}</span>")
        return True

    def on_clock_button_clicked(self, button):
        if not self.backend.username or not self.backend.encrypted_password:
            self.show_error_dialog("Configuração Necessária", 
                                  "Por favor, configure seu usuário e senha primeiro.")
            self.on_settings_clicked(None)
            return
        
        # Ask for confirmation before registering time
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Confirmação"
        )
        confirm_dialog.format_secondary_text("Bater ponto agora?")
        response = confirm_dialog.run()
        confirm_dialog.destroy()
        
        # If user doesn't confirm, return without registering time
        if response != Gtk.ResponseType.YES:
            return
        
        self.status_label.set_text("Registrando ponto...")
        
        # Process UI events to update the status label
        while Gtk.events_pending():
            Gtk.main_iteration()
        
        # Register time using backend
        success, message, current_time = self.backend.register_time()
        
        if success:
            self.show_info_dialog("Sucesso", message)
            self.status_label.set_text(f"Último registro: {current_time}")
        else:
            self.show_error_dialog("Erro", message)
            self.status_label.set_text("Falha ao registrar ponto.")

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
        username_entry.set_text(self.backend.username)
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
            
            # Update credentials using backend
            success, message = self.backend.update_credentials(new_username, new_password if new_password else None)
            self.status_label.set_text(message)
        
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
    app = PontoAppGTK(auto_trigger=args.auto)
    app.run()
