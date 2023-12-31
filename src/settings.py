from utilities import load_object, save_object
import os


class Settings:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.dimensions = (800, 800)
        self.highlight = (-217, -55, -7)
        self.text_color = (38, 28, 55)
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.load_settings()

    def load_settings(self):
        previous_settings = load_object(os.path.join(self.root_dir, self.file_path))
        if previous_settings is not None:
            self.__dict__.update(previous_settings.__dict__)
        else:
            self.load_default_settings()

    def load_default_settings(self):
        default_settings = load_object(os.path.join(self.root_dir, "default_settings.pkl"))
        self.__dict__.update(default_settings.__dict__)

    def save_settings(self):
        save_object(self, self.file_path)
