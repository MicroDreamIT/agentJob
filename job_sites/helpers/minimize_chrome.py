import time

import pyautogui


def minimize_chrome():
    # Command + M is the shortcut to minimize a window in macOS
    pyautogui.hotkey('command', 'm')
    print('minimize did not worked')
    time.sleep(1)  # Wait a bit to ensure the command is processed