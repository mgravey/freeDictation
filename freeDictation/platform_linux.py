# platform_linux.py

from .common_code import FreeDictationAppBase, get_available_models, flagList, save_config
import threading
import pystray
from PIL import Image, ImageDraw
import keyboard  # Requires 'keyboard' package

class FreeDictationApp(FreeDictationAppBase):
    def __init__(self):
        super().__init__()
        # Build the menus
        self.build_menus()
        # Create the icon image and initialize the icon
        self.icon = pystray.Icon("FreeDictation", icon=self.create_image(), menu=self.icon_menu)
        # Start loading the model
        threading.Thread(target=self.load_model).start()
        # Start key event listener
        self.start_key_listener()

    def build_menus(self):
        # Build the Microphone submenu
        self.input_devices = self.get_input_devices()
        microphone_menu_items = []
        for idx, device in self.input_devices.items():
            item = pystray.MenuItem(
                f"{device['name']}",
                self.on_select_input_device,
                checked=lambda item, idx=idx: idx == self.INPUT_DEVICE_INDEX
            )
            item.device_index = idx
            microphone_menu_items.append(item)
        self.microphone_menu = pystray.Menu(*microphone_menu_items)

        # Build the Model submenu
        self.model_names = get_available_models()
        model_menu_items = []
        for name in self.model_names:
            item = pystray.MenuItem(
                name,
                self.on_select_model,
                checked=lambda item, name=name: name == self.MODEL_NAME
            )
            item.model_name = name
            model_menu_items.append(item)
        self.model_menu = pystray.Menu(*model_menu_items)

        # Build the Language submenu
        language_menu_items = []
        if self.languages:
            for name, code in self.languages.items():
                flag = flagList.get(name, '🌐')
                item = pystray.MenuItem(
                    f"{flag} {name}",
                    self.on_select_language,
                    checked=lambda item, name=name: name == self.config["preferred_language"]
                )
                item.language = name
                language_menu_items.append(item)
        else:
            # Provide a default language option if languages are not available
            item = pystray.MenuItem(
                "English",
                self.on_select_language,
                checked=lambda item: "English" == self.config["preferred_language"]
            )
            item.language = "English"
            language_menu_items.append(item)
        self.language_menu = pystray.Menu(*language_menu_items)

        # Build the icon menu
        self.icon_menu = pystray.Menu(
            pystray.MenuItem("Microphone", self.microphone_menu),
            pystray.MenuItem("Model", self.model_menu),
            pystray.MenuItem("Language", self.language_menu),
            pystray.MenuItem("Quit", self.on_quit)
        )

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

    def on_select_input_device(self, item):
        self.select_input_device(item.device_index)
        # Save preferred microphone to config
        device_name = self.input_devices[item.device_index]['name']
        self.config["preferred_microphones"] = [device_name]
        save_config(self.config)
        # Rebuild the menus to update checkmarks
        self.build_menus()
        self.icon.menu = self.icon_menu  # Update the icon menu

    def on_select_model(self, item):
        self.select_model(item.model_name)
        # Rebuild the menus to update checkmarks
        self.build_menus()
        self.icon.menu = self.icon_menu  # Update the icon menu

    def on_select_language(self, item):
        self.select_language(item.language)
        # Rebuild the menus to update checkmarks
        self.build_menus()
        self.icon.menu = self.icon_menu  # Update the icon menu

    def on_quit(self):
        self.icon.stop()


    def start_key_listener(self):
        # Wait for the model to load before starting the key listener
        threading.Thread(target=self.model_loaded_event.wait).start()
        # Start listening for key events
        threading.Thread(target=self.key_event_loop, daemon=True).start()

    def key_event_loop(self):
        # Define the key combination
        COMBINATION = 'ctrl+alt+space'

        # Wait for the model to load
        self.model_loaded_event.wait()

        while True:
            keyboard.wait(COMBINATION)
            self.start_recording()
            keyboard.wait(COMBINATION)
            self.stop_recording()

    def run(self):
        self.icon.run()

    def update_icon(self, status):
        # Implement icon update if needed
        pass
