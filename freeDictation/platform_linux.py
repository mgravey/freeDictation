from .common_code import FreeDictationAppBase, get_available_models
import threading
import pystray
from PIL import Image, ImageDraw
import keyboard  # Requires 'keyboard' package

class FreeDictationApp(FreeDictationAppBase):
    def __init__(self):
        super().__init__()
        # Create system tray icon
        self.icon = pystray.Icon("FreeDictation")
        self.icon.menu = pystray.Menu(
            pystray.MenuItem("Microphone", self.on_microphone_selected),
            pystray.MenuItem("Model", self.on_model_selected),
            pystray.MenuItem("Language", self.on_language_selected),
            pystray.MenuItem("Quit", self.on_quit)
        )
        self.icon.icon = self.create_image()
        # Start key event listener
        self.start_key_listener()
        self.update_device_checkmarks()

    def create_image(self):
        # Create an icon image
        width = 64
        height = 64
        color1 = "black"
        color2 = "white"

        image = Image.new("RGB", (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            [(width // 2, 0), (width, height // 2)],
            fill=color2
        )
        return image

    def on_microphone_selected(self):
        pass  # Implement microphone selection

    def on_model_selected(self):
        pass  # Implement model selection

    def on_language_selected(self):
        pass  # Implement language selection

    def update_languages_menu(self):
        # Recreate the language menu
        language_menu = pystray.Menu(
            *(pystray.MenuItem(f"{flagList.get(name, '🌐')} {name}", self.on_select_language) for name in self.languages.keys())
        )
        # Update the icon menu
        self.icon.menu = pystray.Menu(
            pystray.MenuItem("Microphone", self.on_microphone_selected),
            pystray.MenuItem("Model", self.on_model_selected),
            pystray.MenuItem("Language", language_menu),
            pystray.MenuItem("Quit", self.on_quit)
        )


    def on_quit(self):
        self.icon.stop()

    def start_key_listener(self):
        # Start listening for key events
        threading.Thread(target=self.key_event_loop, daemon=True).start()

    def key_event_loop(self):
        # Define the key combination
        COMBINATION = {'ctrl', 'alt', 'space'}

        while True:
            keyboard.wait('+'.join(COMBINATION))
            self.start_recording()
            keyboard.wait('-'.join(COMBINATION))
            self.stop_recording()

    def run(self):
        self.icon.run()

