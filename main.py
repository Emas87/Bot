import os
from Finder import Finder
from ScreenReader import ScreenReader
import time
import threading
import multiprocessing


class Bot:
    def __init__(self, debug=False):
        self.debug = debug
        self.screen_reader = ScreenReader(debug=debug)
        self.templates = [os.path.abspath(os.path.join('images', 'Mining', path)) for path in os.listdir('images/Mining')]
        self.finder = Finder(self.templates, debug=debug)
        self.finder.load_templates()

    def get_boxes(self):

        # screen_shot = self.screen_reader.background_screenshot()
        windows_pos = self.screen_reader.get_windows_position()
        # This takes a little bit more time
        screen_shot = self.screen_reader.foreground_screenshot()

        self.finder.base_cv_rgb = screen_shot
        self.finder.find_images(offset=(windows_pos[0], windows_pos[1]))
        self.finder.draw_rentangles()

    def keep_getting_boxes(self):
        i = 0
        all_processes = []
        while i < 20:
            process = multiprocessing.Process(target=self.get_boxes)
            process.start()
            all_processes.append(process)
            # t = threading.Thread(target=self.get_boxes)
            time.sleep(1.6)
            i += 1

        for process in all_processes:
            process.terminate()


if __name__ == "__main__":
    bot = Bot()
    bot.keep_getting_boxes()
