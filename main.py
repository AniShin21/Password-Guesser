from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.filechooser import FileChooserIconView
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.app import MDApp
from kivy.clock import Clock
import time


class TestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.passwords = []
        self.index = 0  # Start from the first password
        self.bin = []  # To store invalid passwords
        self.speed = 1  # Speed control: 1 password per second (default)

        self.test_status_label = Label(text="Ready to start testing.", size_hint=(None, None), pos=(100, 300))
        self.add_widget(self.test_status_label)

        # Add "Start" button
        start_button = MDRaisedButton(text="Start", pos=(100, 200), on_release=self.start_testing)
        self.add_widget(start_button)

        # Add "Stop" button
        stop_button = MDRaisedButton(text="Stop", pos=(200, 200), on_release=self.stop_testing)
        self.add_widget(stop_button)

        # Add "Load File" button
        load_file_button = MDRaisedButton(text="Load File", pos=(100, 150), on_release=self.load_file)
        self.add_widget(load_file_button)

    def load_file(self, instance):
        # Open the file chooser to pick a .txt file
        file_chooser = FileChooserIconView()
        file_chooser.bind(on_selection=self.load_passwords_from_file)
        self.add_widget(file_chooser)

    def load_passwords_from_file(self, filechooser, selection):
        # If a file is selected, load the passwords
        if selection:
            file_path = selection[0]
            with open(file_path, 'r') as file:
                self.passwords = file.read().splitlines()
            self.index = 0  # Reset index
            self.bin = []  # Clear invalid bin
            self.test_status_label.text = f"Loaded {len(self.passwords)} passwords."
            print(f"Passwords loaded: {self.passwords}")

    def start_testing(self, instance):
        if not self.passwords:
            self.test_status_label.text = "No passwords to test."
            return
        self.test_status_label.text = f"Testing password {self.index + 1}/{len(self.passwords)}"
        Clock.schedule_once(self.test_next_password, 1 / self.speed)  # Start testing with specified speed

    def stop_testing(self, instance):
        self.test_status_label.text = "Testing paused."
        Clock.unschedule(self.test_next_password)  # Stop the test when pressed

    def test_next_password(self, dt):
        if self.index < len(self.passwords):
            current_password = self.passwords[self.index]
            # Simulate password testing
            valid = self.simulate_password_test(current_password)  # Placeholder method to simulate the test

            if not valid:
                self.bin.append(current_password)  # Invalid password
            self.index += 1
            self.test_status_label.text = f"Testing password {self.index + 1}/{len(self.passwords)}"
            if self.index < len(self.passwords):
                Clock.schedule_once(self.test_next_password, 1 / self.speed)
            else:
                self.test_status_label.text = "Testing complete."
        else:
            self.test_status_label.text = "No more passwords to test."

    def simulate_password_test(self, password):
        # This is a placeholder for your password testing logic
        # Simulate that passwords ending in '123' are invalid
        return not password.endswith('123')

    def view_bin(self):
        # Method to show the bin (invalid passwords)
        bin_dialog = MDDialog(title="Invalid Passwords", text=str(self.bin), size_hint=(0.8, 0.4))
        bin_dialog.open()


class FloatingButton(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_screen = TestScreen(name="test_screen")

        # Floating action button (FAB)
        self.fab = MDRaisedButton(text="Test", size_hint=(None, None), size=(100, 100), pos=(10, 10),
                                  on_release=self.toggle_test_screen)
        self.add_widget(self.fab)

        # Add a button for viewing the bin
        bin_button = MDRaisedButton(text="View Bin", size_hint=(None, None), size=(100, 50), pos=(150, 10),
                                    on_release=self.test_screen.view_bin)
        self.add_widget(bin_button)

    def toggle_test_screen(self, instance):
        # Switch to the TestScreen when clicked
        app = MDApp.get_running_app()
        app.screen_manager.current = 'test_screen'


class MyApp(MDApp):
    def build(self):
        self.screen_manager = ScreenManager()
        self.floating_button = FloatingButton()
        self.screen_manager.add_widget(self.floating_button)
        self.screen_manager.add_widget(self.floating_button.test_screen)

        return self.screen_manager

    def on_start(self):
        # Placeholder for loading a default file or testing
        pass

    def on_pause(self):
        return True  # Keep the app running in the background


if __name__ == '__main__':
    MyApp().run()
