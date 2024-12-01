import os

root = os.path.dirname(__file__)

def get_ui_path(filename):
    return os.path.join(root, "ui", filename)
