import os
from kivy.app import App
from kivy.uix.filechooser import FileChooserListView
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.floatlayout import FloatLayout
from kivymd.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.dialog import MDDialog
from kivy.uix.behaviors import DragBehavior
from threading import Thread
import time
import shutil

class DraggableButton(DragBehavior, MDRaisedButton):
    """This class creates a draggable button that can float over the screen."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''  # Remove button background
        self.background_color = (0, 0, 1, 1)  # Blue color
        self.size_hint = None, None
        self.size = (80, 80)  # Set the size to a smaller circle
        self.text = "Start"  # Default text for the floating button

class MainScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.file_path = None  # Path to the password file
        self.passwords = []  # List of passwords from the file
        self.current_index = 0  # Tracks current password being tested
        self.invalid_passwords = []  # Passwords added to the bin
        self.running = False  # Controls the password testing loop
        self.last_tested_password = None  # Tracks the last tested password
        self.hovering_btn = None
        self.status_label = None
        self.test_options = None  # To hold the test options UI

        self.layout = FloatLayout()
        self.create_widgets()

        self.add_widget(self.layout)

        self.create_downloads_folder()  # Ensure folder exists in Downloads

    def create_widgets(self):
        """Create all the widgets for the main screen."""
        # Get Button to show the hovering button
        get_button = MDRaisedButton(text="Get Button", size_hint=(None, None), size=(200, 50), pos_hint={'x': 0.1, 'y': 0.8})
        get_button.bind(on_press=self.show_hover_button)
        self.layout.add_widget(get_button)

        # Bin Button
        bin_button = MDRaisedButton(text="Bin", size_hint=(None, None), size=(200, 50), pos_hint={'x': 0.1, 'y': 0.6})
        bin_button.bind(on_press=self.view_bin)
        self.layout.add_widget(bin_button)

        # Load File Button
        load_file_button = MDRaisedButton(text="Load File", size_hint=(None, None), size=(200, 50), pos_hint={'x': 0.1, 'y': 0.4})
        load_file_button.bind(on_press=self.load_file_popup)
        self.layout.add_widget(load_file_button)

        # Status Label for keyboard (if visible or hidden)
        self.status_label = MDLabel(text="Keyboard Status: Hidden", size_hint=(None, None), size=(200, 50), pos_hint={'x': 0.1, 'y': 0.2})
        self.layout.add_widget(self.status_label)

    def create_downloads_folder(self):
        """Check if folder exists in Downloads, if not, create it."""
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        app_folder_path = os.path.join(downloads_path, "PasswordApp")

        if not os.path.exists(app_folder_path):
            os.makedirs(app_folder_path)

        self.app_folder_path = app_folder_path  # Store the path for later use

    def show_hover_button(self, instance):
        """This function will create and show the floating button when the 'Get Button' is pressed."""
        if not self.hovering_btn:
            self.hovering_btn = DraggableButton(pos_hint={'x': 0.7, 'y': 0.8})
            self.hovering_btn.bind(on_press=self.toggle_test_options)
            self.layout.add_widget(self.hovering_btn)

    def toggle_test_options(self, instance):
        """Show or hide the options when the hovering button is clicked."""
        if self.test_options:
            self.layout.remove_widget(self.test_options)
            self.test_options = None
        else:
            self.test_options = FloatLayout()

            start_button = MDRaisedButton(text="Start", size_hint=(None, None), size=(150, 50), pos_hint={'x': 0.3, 'y': 0.7})
            start_button.bind(on_press=self.start_typing)
            self.test_options.add_widget(start_button)

            stop_button = MDRaisedButton(text="Stop", size_hint=(None, None), size=(150, 50), pos_hint={'x': 0.3, 'y': 0.5})
            stop_button.bind(on_press=self.stop_typing)
            self.test_options.add_widget(stop_button)

            stats_button = MDRaisedButton(text="Stats", size_hint=(None, None), size=(150, 50), pos_hint={'x': 0.3, 'y': 0.3})
            stats_button.bind(on_press=self.show_stats)
            self.test_options.add_widget(stats_button)

            self.layout.add_widget(self.test_options)

    def start_typing(self, instance):
        """Start typing passwords."""
        if not self.file_path or self.current_index >= len(self.passwords):
            self.show_popup("Error", "No passwords to test. Load a file first.")
            return

        self.running = True
        Thread(target=self.type_passwords).start()

    def stop_typing(self, instance):
        """Stop the password testing."""
        self.running = False
        self.show_popup("Info", "Password testing stopped.")

    def type_passwords(self):
        """Simulate typing the passwords with a delay between each one."""
        while self.running and self.current_index < len(self.passwords):
            password = self.passwords[self.current_index]
            self.last_tested_password = password  # Keep track of the last tested password

            # Add to bin if password doesn't work (simulated logic)
            self.invalid_passwords.append(password)

            self.current_index += 1
            time.sleep(0.2)

        if self.current_index >= len(self.passwords):
            self.show_popup("Info", "All passwords tested. Check the bin for potential passwords.")
        self.running = False

    def show_popup(self, title, message):
        """Show a popup using MDDialog."""
        dialog = MDDialog(title=title, text=message, size_hint=(0.8, 0.5))
        dialog.open()

    def load_file_popup(self, instance):
        """Open file chooser popup to load the password file."""
        content = FileChooserListView(on_submit=self.load_file, filters=["*.txt"])
        filechooser_popup = Popup(title="Select Password File", content=content, size_hint=(0.9, 0.9))
        content.popup = filechooser_popup
        filechooser_popup.open()

    def load_file(self, filechooser, selection, touch=None):
        """Load the file and process passwords."""
        if selection:
            self.file_path = selection[0]
            destination = os.path.join(self.app_folder_path, os.path.basename(self.file_path))
            shutil.copy(self.file_path, destination)

            with open(destination, 'r') as file:
                self.passwords = [line.strip() for line in file if len(line.strip()) == 6 and line.strip().isdigit()]

            if not self.passwords:
                self.show_popup("Error", "No valid 6-digit passwords found in the file.")
                self.file_path = None
            else:
                self.current_index = 0
                self.show_popup("Success", f"Loaded {len(self.passwords)} valid passwords from file.")
        
        filechooser.popup.dismiss()

    def show_stats(self, instance):
        """Show the stats of tested passwords."""
        stats_message = f"Tested {self.current_index}/{len(self.passwords)} passwords."
        self.show_popup("Stats", stats_message)

    def view_bin(self, instance):
        """View the bin of invalid passwords."""
        bin_content = "\n".join(self.invalid_passwords) if self.invalid_passwords else "No invalid passwords yet."
        self.show_popup("Bin", bin_content)

class PasswordApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(app=self, name="main"))
        return sm

if __name__ == "__main__":
    PasswordApp().run()
