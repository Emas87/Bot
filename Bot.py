import os
from Finder import Finder
from ScreenReader import ScreenReader
from MouseController import MouseController
import time
import multiprocessing
import numpy
import json
import glob


class Bot:
    def __init__(self, debug=False):
        self.image_dict = {}
        self.mouse_controller = MouseController()
        self.debug = debug
        self.finder = Finder(debug=debug)
        self.screen_reader = ScreenReader(debug=debug)
        with open("config/config.json") as input_file:
            self.config = json.load(input_file)

        self.load_images_from_config()

    def load_images_from_config(self):
        for category, directories in self.config["img_categories"].items():
            for directory, files in directories.items():
                for image in files:
                    files_path = os.path.abspath(os.path.join("images", directory, image))
                    glob_files = glob.glob(files_path)
                    for glob_file in glob_files:
                        self.add_image_2_dict(glob_file, category)

    def add_image_2_dict(self, image, key):
        loaded_image = self.finder.load_images([image])
        if key not in self.image_dict:
            self.image_dict[key] = [loaded_image]
        else:
            self.image_dict[key].append(loaded_image)

    def get_boxes(self):

        screen_shot = self.screen_reader.background_screenshot()
        windows_pos = self.screen_reader.get_windows_position()
        # This takes a little bit more time
        # screen_shot = self.screen_reader.foreground_screenshot()

        self.finder.find_images(screen_shot, self.image_dict["ores"], offset=(windows_pos[0], windows_pos[1]))

    def keep_drawing_boxes(self):
        i = 0
        all_processes = []
        while i < 20:
            self.get_boxes()
            process = multiprocessing.Process(target=self.finder.draw_rentangles)
            process.start()
            all_processes.append(process)
            time.sleep(1.6)
            i += 1

        for process in all_processes:
            process.terminate()

    def keep_clicking(self):
        i = 0
        while i < 20:
            self.get_boxes()
            x, y, status = self.get_closer_center()
            if status:
                self.mouse_controller.click(x, y)
            time.sleep(1)
            i += 1

    def get_closer_center(self):
        if len(self.finder.centers) > 0:
            # base position
            pos_base = (10000, 10000)
            windows_pos = self.screen_reader.get_windows_position()
            x_player, y_player, status = self.finder.find_player(offset=(windows_pos[0], windows_pos[1]))
            if not status:
                return 0, 0, False
            for center in self.finder.centers:
                # Distance between two points formula
                distance_base = numpy.sqrt(
                    numpy.power(x_player - pos_base[0], 2) + numpy.power(y_player - pos_base[1], 2))
                distance_to_center = numpy.sqrt(
                    numpy.power(x_player - center[0], 2) + numpy.power(y_player - center[1], 2))
                if distance_to_center < distance_base:
                    pos_base = (center[0], center[1])
            return pos_base[0], pos_base[1], True
        return 0, 0, False


if __name__ == "__main__":
    bot = Bot()
    bot.keep_clicking()
