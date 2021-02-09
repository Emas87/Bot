
from PIL import ImageGrab
import win32gui
import win32ui
import win32con
import time


class ScreenReader:
    def __init__(self, program_title='ldplayer(64)'):
        self.program_title = program_title
        self.debug = False

    def foreground_screenshot(self):
        window_handle = win32gui.FindWindow(None, self.program_title.lower())
        win32gui.SetForegroundWindow(window_handle)
        bbox = win32gui.GetWindowRect(window_handle)
        img = ImageGrab.grab(bbox)
        return img

    def get_windows_position(self):
        window_handle = win32gui.FindWindow(None, self.program_title.lower())
        bbox = win32gui.GetWindowRect(window_handle)
        return bbox[0], bbox[1]

    @staticmethod
    def get_mouse_position():
        position = win32gui.GetCursorPos()
        print(position)
        time.sleep(1)

    def background_screenshot(self):
        window_handle = win32gui.FindWindow(None, self.program_title.lower())
        bbox = win32gui.GetWindowRect(window_handle)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        wdc = win32gui.GetWindowDC(window_handle)
        dcobj = win32ui.CreateDCFromHandle(wdc)
        cdc = dcobj.CreateCompatibleDC()
        databitmap = win32ui.CreateBitmap()
        databitmap.CreateCompatibleBitmap(dcobj, width, height)
        cdc.SelectObject(databitmap)
        cdc.BitBlt((0, 0), (width, height), dcobj, (0, 0), win32con.SRCCOPY)
        if self.debug:
            databitmap.SaveBitmapFile(cdc, 'screenshot.bmp')
        dcobj.DeleteDC()
        cdc.DeleteDC()
        win32gui.ReleaseDC(window_handle, wdc)
        win32gui.DeleteObject(databitmap.GetHandle())
        return databitmap


if __name__ == "__main__":
    screen_reader = ScreenReader()
    # screen_reader.foreground_screenshot()
    screen_reader.background_screenshot()
    print(screen_reader.get_windows_position())
    screen_reader.get_mouse_position()
