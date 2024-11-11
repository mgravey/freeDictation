# platform_mac.py

from .common_code import FreeDictationAppBase, get_available_models, flagList, CONFIG_PATH
import rumps
import threading
from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
import Quartz
import subprocess
import os

class FreeDictationApp(FreeDictationAppBase, rumps.App):
    def __init__(self):
        # Initialize rumps.App with a default title
        rumps.App.__init__(self, "⏸")
        FreeDictationAppBase.__init__(self)

        # Build the menu
        self.menu = [
            "Microphone",
            None,  # Separator
            "Model",
            None,  # Separator
        ]

        # Build the Microphone submenu
        self.input_devices = self.get_input_devices()
        self.device_menu_items = []
        for idx, device in self.input_devices.items():
            item = rumps.MenuItem(f"{device['name']}", callback=self.on_select_input_device)
            item.device_index = idx
            self.device_menu_items.append(item)
            self.menu["Microphone"].add(item)

        # Apply microphone preferences
        preferred_mics = self.config.get("preferred_microphones", [])
        self.select_preferred_microphone(preferred_mics)
        self.update_device_checkmarks()

        # Build the Model submenu
        self.model_names = get_available_models()
        self.model_menu_items = []
        for name in self.model_names:
            item = rumps.MenuItem(name, callback=self.on_select_model)
            item.model_name = name
            self.model_menu_items.append(item)
            self.menu["Model"].add(item)
        self.update_model_checkmarks()

        # Add 'Language' menu
        self.menu.add(rumps.MenuItem("Language"))
        self.menu["Language"].add(rumps.separator) 
        self.update_languages_menu()

        # Add 'Open Config File' menu item after 'Language'
        self.menu.insert_after('Language', rumps.MenuItem('Open Config File', callback=self.open_config_file))

        # Load the model after menus are initialized
        threading.Thread(target=self.load_model).start()

    def run(self, *args, **kwargs):
        # Set the activation policy after NSApplication has been initialized
        NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        super(FreeDictationApp, self).run(*args, **kwargs)

    def on_select_input_device(self, sender):
        self.select_input_device(sender.device_index)
        # Save the preferred microphone to config
        device_name = self.input_devices[sender.device_index]['name']
        self.config["preferred_microphones"] = [device_name]  # Update preference
        save_config(self.config)
        self.update_device_checkmarks()

    def update_device_checkmarks(self):
        for item in self.device_menu_items:
            item.state = 1 if item.device_index == self.INPUT_DEVICE_INDEX else 0

    def on_select_model(self, sender):
        self.select_model(sender.model_name)
        self.update_model_checkmarks()

    def update_model_checkmarks(self):
        for item in self.model_menu_items:
            item.state = 1 if item.model_name == self.MODEL_NAME else 0

    def on_select_language(self, sender):
        self.select_language(sender.language)
        self.update_language_checkmarks()

    def update_language_checkmarks(self):
        for item in self.language_menu_items:
            item.state = 1 if item.language == self.config["preferred_language"] else 0

    def update_languages_menu(self):
        # Ensure 'Language' menu exists
        if "Language" not in self.menu:
            self.menu.add(rumps.MenuItem("Language"))

        # Clear old language menu items
        self.menu["Language"].clear()
        self.language_menu_items = []

        for name, code in self.languages.items():
            flag = flagList.get(name, '🌐')
            item = rumps.MenuItem(f"{flag} {name}", callback=self.on_select_language)
            item.language = name
            self.language_menu_items.append(item)
            self.menu["Language"].add(item)
        self.update_language_checkmarks()

    def update_icon(self, status):
        # Update the menu bar icon based on status
        if status == "idle":
            self.title = "⏸"
        elif status == "recording":
            self.title = "👂"
        elif status == "transcribing":
            self.title = "💭"
        elif status == "error":
            self.title = "🛑"
        elif status == "loading":
            self.title = "⏳"
        else:
            self.title = "❓"

    def open_config_file(self, _):
        # Use subprocess to open the config file with the default editor
        config_path = os.path.abspath(CONFIG_PATH)
        try:
            subprocess.call(['open', config_path])
        except Exception as e:
            print(f"Failed to open config file: {e}")

    # Key event handling using Quartz
    def run_event_loop(self):
        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGTailAppendEventTap,
            Quartz.kCGEventTapOptionDefault,
            Quartz.kCGEventMaskForAllEvents,
            self.handle_event,
            None
        )
        loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
        Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), loop_source, Quartz.kCFRunLoopCommonModes)
        Quartz.CGEventTapEnable(tap, True)
        print("Listening for key events...")
        Quartz.CFRunLoopRun()

    def handle_event(self, proxy, event_type, event, refcon):
        if event_type == Quartz.kCGEventKeyDown:
            key_code = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
            flags = Quartz.CGEventGetFlags(event)

            # Check if Ctrl + Alt + Cmd + Space is pressed
            if (key_code == 49  # Space key
                    and (flags & Quartz.kCGEventFlagMaskControl)
                    and (flags & Quartz.kCGEventFlagMaskAlternate)
                    and (flags & Quartz.kCGEventFlagMaskCommand)):
                # Start recording
                self.start_recording()
                return None  # Suppress the system event

        elif event_type == Quartz.kCGEventKeyUp:
            key_code = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
            flags = Quartz.CGEventGetFlags(event)

            # Check if Ctrl + Alt + Cmd + Space is released
            if (key_code == 49  # Space key
                    and (flags & Quartz.kCGEventFlagMaskControl)
                    and (flags & Quartz.kCGEventFlagMaskAlternate)
                    and (flags & Quartz.kCGEventFlagMaskCommand)):
                self.stop_recording()
                return None  # Suppress the system event

        return event  # Pass the event along

    def run(self):
        # Set the activation policy after NSApplication has been initialized
        NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        # Start the event loop in a separate thread
        event_loop_thread = threading.Thread(target=self.run_event_loop, daemon=True)
        event_loop_thread.start()
        # Call the run method of rumps.App directly
        rumps.App.run(self)
