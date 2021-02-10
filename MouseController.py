import logging

import win32api
import win32con


class MouseController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def click(x, y):
        x = int(x)
        y = int(y)
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    @staticmethod
    def drag(x1, y1, x2, y2):
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)
        win32api.SetCursorPos((x1, y1))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x1, y1, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x2, y2, 0, 0)
