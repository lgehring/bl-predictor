"""
Run the application.

This module is invoked when calling ``python -m bl_predictor``.
"""
from bl_predictor import gui

if __name__ == '__main__':
    gui.MainWindow(None).show_window()


def main():
    gui.MainWindow(None).show_window()
