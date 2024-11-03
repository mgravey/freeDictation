import sounddevice as sd
import numpy as np
import threading
import whisper
import json
import os
import tempfile
import soundfile as sf
from pynput import keyboard
from pynput.keyboard import Controller, Key
import time


# Define flagList for emojis
flagList = {
    'Auto-Detect': '🌐',
    'English': '🇬🇧',
    'Chinese': '🇨🇳',
    'German': '🇩🇪',
    'Spanish': '🇪🇸',
    'Russian': '🇷🇺',
    'Korean': '🇰🇷',
    'French': '🇫🇷',
    'Japanese': '🇯🇵',
    'Portuguese': '🇵🇹',
    'Turkish': '🇹🇷',
    'Polish': '🇵🇱',
    'Catalan': '🌐',
    'Dutch': '🇳🇱',
    'Arabic': '🇦🇪',
    'Swedish': '🇸🇪',
    'Italian': '🇮🇹',
    'Indonesian': '🇮🇩',
    'Hindi': '🇮🇳',
    'Finnish': '🇫🇮',
    'Vietnamese': '🇻🇳',
    'Hebrew': '🇮🇱',
    'Ukrainian': '🇺🇦',
    'Greek': '🇬🇷',
    'Malay': '🇲🇾',
    'Czech': '🇨🇿',
    'Romanian': '🇷🇴',
    'Danish': '🇩🇰',
    'Hungarian': '🇭🇺',
    'Tamil': '🇮🇳',
    'Norwegian': '🇳🇴',
    'Thai': '🇹🇭',
    'Urdu': '🇵🇰',
    'Croatian': '🇭🇷',
    'Bulgarian': '🇧🇬',
    'Lithuanian': '🇱🇹',
    'Latin': '🏛️',
    'Maori': '🇳🇿',
    'Malayalam': '🇮🇳',
    'Welsh': '🌐',
    'Slovak': '🇸🇰',
    'Telugu': '🇮🇳',
    'Persian': '🇮🇷',
    'Latvian': '🇱🇻',
    'Bengali': '🇧🇩',
    'Serbian': '🇷🇸',
    'Azerbaijani': '🇦🇿',
    'Slovenian': '🇸🇮',
    'Kannada': '🇮🇳',
    'Estonian': '🇪🇪',
    'Macedonian': '🇲🇰',
    'Breton': '🌐',
    'Basque': '🌐',
    'Icelandic': '🇮🇸',
    'Armenian': '🇦🇲',
    'Nepali': '🇳🇵',
    'Mongolian': '🇲🇳',
    'Bosnian': '🇧🇦',
    'Kazakh': '🇰🇿',
    'Albanian': '🇦🇱',
    'Swahili': '🇰🇪',
    'Galician': '🇪🇸',
    'Marathi': '🇮🇳',
    'Punjabi': '🇮🇳',
    'Sinhala': '🇱🇰',
    'Khmer': '🇰🇭',
    'Shona': '🇿🇼',
    'Yoruba': '🇳🇬',
    'Somali': '🇸🇴',
    'Afrikaans': '🇿🇦',
    'Occitan': '🌐',
    'Georgian': '🇬🇪',
    'Belarusian': '🇧🇾',
    'Tajik': '🇹🇯',
    'Sindhi': '🇵🇰',
    'Gujarati': '🇮🇳',
    'Amharic': '🇪🇹',
    'Yiddish': '🕍',
    'Lao': '🇱🇦',
    'Uzbek': '🇺🇿',
    'Faroese': '🇫🇴',
    'Haitian Creole': '🇭🇹',
    'Pashto': '🇦🇫',
    'Turkmen': '🇹🇲',
    'Nynorsk': '🇳🇴',
    'Maltese': '🇲🇹',
    'Sanskrit': '🕉️',
    'Luxembourgish': '🇱🇺',
    'Myanmar': '🇲🇲',
    'Tibetan': '🏔️',
    'Tagalog': '🇵🇭',
    'Malagasy': '🇲🇬',
    'Assamese': '🇮🇳',
    'Tatar': '🇷🇺',
    'Hawaiian': '🌺',
    'Lingala': '🇨🇩',
    'Hausa': '🇳🇬',
    'Bashkir': '🇷🇺',
    'Javanese': '🇮🇩',
    'Sundanese': '🇮🇩',
    'Cantonese': '🇭🇰'
}

# Define supported languages
supported_languages_multilingual = {"Auto-Detect": None} | {v.capitalize(): k for k, v in whisper.tokenizer.LANGUAGES.items()}
supported_languages_english_only = {"English": "en"}

# Path to the configuration file
CONFIG_PATH = "config.json"

# Load configuration file or use default settings
def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as config_file:
                config = json.load(config_file)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse config file '{CONFIG_PATH}': {e}")
            print("Using default configuration.")
            config = {
                "preferred_microphones": [],
                "preferred_model": "base",
                "preferred_language": "Auto-Detect"
            }
    else:
        # Default config if no config file exists
        config = {
            "preferred_microphones": [],
            "preferred_model": "base",
            "preferred_language": "Auto-Detect"
        }
    return config

# Save configuration to file
def save_config(config):
    with open(CONFIG_PATH, 'w') as config_file:
        json.dump(config, config_file, indent=4)

# Function to get available Whisper models
def get_available_models():
    return list(whisper._MODELS.keys())

# Base class for FreeDictationApp
class FreeDictationAppBase:
    def __init__(self):
        self.config = load_config()
        self.selected_language = self.config.get("preferred_language", "Auto-Detect")
        self.MODEL_NAME = self.config.get("preferred_model", "base")
        self.INPUT_DEVICE_INDEX = None
        self.model = None
        self.recording = False
        self.audio_data = []
        self.keyboard_controller = Controller()
        self.load_model()
        self.input_devices = self.get_input_devices()
        preferred_mics = self.config.get("preferred_microphones", [])
        self.select_preferred_microphone(preferred_mics)

    def load_model(self):
        print(f"Loading model '{self.MODEL_NAME}'...")
        try:
            self.model = whisper.load_model(self.MODEL_NAME)
            print(f"Model '{self.MODEL_NAME}' loaded successfully.")
            # Update language menu based on model
            if self.MODEL_NAME.endswith('.en'):
                self.languages = supported_languages_english_only
            else:
                self.languages = supported_languages_multilingual
            self.update_languages_menu()  # Call method to update the language menu
        except Exception as e:
            print(f"Error loading model '{self.MODEL_NAME}': {e}")
    def update_languages_menu(self):
        pass  # To be implemented in platform-specific subclasses

    def select_preferred_microphone(self, preferred_mics):
        current_best_index = None
        current_best_rank = float('inf')
        for idx, device in self.input_devices.items():
            if device['name'] in preferred_mics:
                rank = preferred_mics.index(device['name'])
                if rank < current_best_rank:
                    current_best_rank = rank
                    current_best_index = idx
        if current_best_index is not None:
            self.INPUT_DEVICE_INDEX = current_best_index
            print(f"Preferred input device selected: {self.input_devices[self.INPUT_DEVICE_INDEX]['name']}")
        else:
            # Default to system default input device
            default_devices = sd.default.device
            if default_devices and default_devices[0] in self.input_devices:
                self.INPUT_DEVICE_INDEX = default_devices[0]
                print(f"Default input device selected: {self.input_devices[self.INPUT_DEVICE_INDEX]['name']}")
            else:
                # If system default not found, select the first available device
                self.INPUT_DEVICE_INDEX = next(iter(self.input_devices))
                print(f"Default input device selected: {self.input_devices[self.INPUT_DEVICE_INDEX]['name']}")


    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.audio_data = []
            threading.Thread(target=self.record_audio).start()
            print("Recording started...")
            self.update_icon("recording")  # Update icon if applicable

    def stop_recording(self):
        if self.recording:
            self.recording = False
            threading.Thread(target=self.transcribe_audio).start()
            print("Recording stopped. Transcribing...")
            self.update_icon("transcribing")  # Update icon if applicable

    def record_audio(self):
        def callback(indata, frames, time_info, status):
            if self.recording:
                self.audio_data.append(indata.copy())

        try:
            with sd.InputStream(
                samplerate=16000,
                channels=1,
                dtype='float32',
                callback=callback,
                device=self.INPUT_DEVICE_INDEX  # Use the selected device
            ):
                while self.recording:
                    sd.sleep(100)
        except Exception as e:
            print(f"Error accessing the microphone: {e}")
            self.update_icon("idle")  # Update icon if applicable

    def transcribe_audio(self):
        if self.audio_data:
            # Combine the audio data into a single NumPy array
            audio_np = np.concatenate(self.audio_data, axis=0)

            # Save the audio to a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav") as tmpfile:
                sf.write(tmpfile.name, audio_np, 16000, format='WAV', subtype='PCM_16')

                # Transcribe with forced language or auto-detect
                transcribe_options = {}
                if self.selected_language and self.selected_language != "Auto-Detect":
                    transcribe_options['language'] = self.selected_language
                transcribe_options["fp16"] = False

                result = self.model.transcribe(tmpfile.name, **transcribe_options)
                text = result['text'].strip()

                # Insert the transcribed text into the active window
                self.insert_text(text)
                print(f"Transcribed Text: {text}")

        self.update_icon("idle")  # Update icon if applicable


    def insert_text(self, text):
        # Simulate typing the text into the active window
        for char in text:
            if char == '\n':
                self.keyboard_controller.press(Key.enter)
                self.keyboard_controller.release(Key.enter)
            elif char == '\t':
                self.keyboard_controller.press(Key.tab)
                self.keyboard_controller.release(Key.tab)
            elif char == '\b':
                self.keyboard_controller.press(Key.backspace)
                self.keyboard_controller.release(Key.backspace)
            else:
                self.keyboard_controller.type(char)
            time.sleep(0.001)  # Adjust as needed

    def get_input_devices(self):
        devices = sd.query_devices()
        input_devices = {}
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices[idx] = device
        return input_devices

    # Abstract methods to be implemented in platform-specific subclasses
    def run(self):
        raise NotImplementedError("Subclasses should implement this!")

    def update_icon(self, status):
        pass  # Optional: Implement platform-specific icon updates

    def select_input_device(self, index):
        self.INPUT_DEVICE_INDEX = index
        print(f"Selected input device: {self.INPUT_DEVICE_INDEX}")

    def select_model(self, model_name):
        if model_name != self.MODEL_NAME:
            self.MODEL_NAME = model_name
            self.config["preferred_model"] = self.MODEL_NAME
            save_config(self.config)
            self.load_model()

    def select_language(self, language_name):
        self.selected_language = self.languages.get(language_name)
        self.config["preferred_language"] = language_name
        save_config(self.config)
