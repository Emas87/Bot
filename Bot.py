import sys
from Finder import Finder
from ImageDict import ImageDict
from ScreenReader import ScreenReader
from MouseController import MouseController
import time
import multiprocessing
import numpy
import json
import logging


class Bot:
    def __init__(self, debug=False):
        if debug:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(filename='logger.log', level=level, filemode="w")

        self.logger = logging.getLogger()
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.image_dict = ImageDict()
        self.mouse_controller = MouseController()
        self.debug = debug
        self.finder = Finder(debug=debug)
        self.screen_reader = ScreenReader(debug=debug)

        # Cofnig file
        with open("config/config.json") as input_file:
            self.config = json.load(input_file)
        self.image_dict.load_images(self.config)

        # Processes
        self.control_process = None

    def get_boxes(self, key, image=None, color=False, threshold=0.85):
        # Will get all matches for the images inside the dict with key 'key'
        screen_shot = self.screen_reader.background_screenshot()
        if screen_shot is None:
            self.logger.error("Couldn't get a screenshot of the program")
            return 0, 0, False
        windows_pos = self.screen_reader.get_windows_position()
        # This takes a little bit more time
        # screen_shot = self.screen_reader.foreground_screenshot()
        if image is not None:
            final_rectangles, final_centers, status = self.finder.find_images(screen_shot, [image],
                                                                              offset=(windows_pos[0], windows_pos[1]),
                                                                              color=color, threshold=threshold)
        else:
            final_rectangles, final_centers, status = self.finder.find_images(screen_shot, self.image_dict.get(key),
                                                                              offset=(windows_pos[0], windows_pos[1]),
                                                                              color=color, threshold=threshold)

        return final_rectangles, final_centers, status

    def keep_drawing_boxes(self, key="ores"):
        i = 0
        all_processes = []
        while i < 10:
            ores_rectangles, ores_centers, status = self.get_boxes(key)
            if not status:
                self.logger.debug("Ores didn't match")
                time.sleep(1)
                i += 1
                continue
            # process = multiprocessing.Process(target=self.finder.draw_rentangles, args=(ores_rectangles,))
            self.finder.draw_rentangles(ores_rectangles)
            # process.start()
            # all_processes.append(process)
            time.sleep(1.6)
            i += 1

        for process in all_processes:
            process.terminate()

    def keep_clicking(self):
        i = 0
        while i < 10:
            _, ores_centers, status = self.get_boxes("ores")
            if not status:
                self.logger.debug("Ores didn't match")
                time.sleep(1)
                continue
            x, y, status = self.get_closest_center(ores_centers)
            if status:
                self.mouse_controller.click(x, y)
            else:
                self.logger.debug("Character didn't match")
            time.sleep(1)
            i += 1

    def get_closest_center(self, ores_centers):
        # get ore closets to player
        if len(ores_centers) > 0:
            _, character_centers, status = self.get_boxes("character")
            if not status or len(character_centers) == 0:
                return 0, 0, False

            # base position
            pos_base = (10000, 10000)
            x_player, y_player = character_centers[0]
            for center in ores_centers:
                # Distance between two points formula
                distance_base = numpy.sqrt(
                    numpy.power(x_player - pos_base[0], 2) + numpy.power(y_player - pos_base[1], 2))
                distance_to_center = numpy.sqrt(
                    numpy.power(x_player - center[0], 2) + numpy.power(y_player - center[1], 2))
                if distance_to_center < distance_base:
                    pos_base = (center[0], center[1])

            return pos_base[0], pos_base[1], True
        return 0, 0, False

    def start(self):
        # self.control_process = multiprocessing.Process(target=self.control_mining)
        # self.control_process.start()
        self.control_mining()

    def stop(self):
        self.control_process.terminate()

    def control_mining(self):
        waiting_time = 1
        ores_centers_save = ()
        enemy_centers_save = ()
        # TODO plan what to do if is stuck, in this case in enemiew, and there is no enemies
        while True:
            # Look for enemies
            _, enemi_centers, status = self.get_boxes("enemies", threshold=0.64)
            if not status:
                self.logger.debug("No enemy found")
            elif len(enemi_centers) > 0:
                # self.measure_time(self.press_action_button, args="pickaxe")
                self.press_button("fight", "weapon")
                self.logger.info("Click in weapon")
                time.sleep(waiting_time/2)
                continue

            # Look for action image
            _, action_centers, status = self.get_boxes("action")
            if not status:
                self.logger.debug("No action found")
            elif len(action_centers) > 0:
                # self.measure_time(self.press_action_button, args="pickaxe")
                self.press_button("tools", "pickaxe")
                self.logger.info("Click in pickaxe")
                time.sleep(waiting_time)
                continue

            # Look for chests, open it and close it
            chest = self.press_button("secuence", "chest")
            while chest:
                chest_button = self.press_button("secuence", "chest_button")
                while chest_button:
                    claim_all = self.press_button("secuence", "claim_all")
                    while claim_all:
                        close = self.press_button("secuence", "close")
                        if close:
                            chest = False
                            chest_button = False
                            break

            # Look for ores
            _, ores_centers, status = self.get_boxes("ores")
            if not status:
                self.logger.debug("Ores didn't match")
                time.sleep(waiting_time)
                continue
            x, y, status = self.get_closest_center(ores_centers)
            if status:
                if ores_centers_save == ores_centers:
                    # This means that ores is in a place where can't be mined
                    self.press_button("tools", "pickaxe")
                ores_centers_save = ores_centers
                self.mouse_controller.click(x, y)
                self.logger.info("Click in ore")
                time.sleep(waiting_time)
                continue
            else:
                self.logger.debug("Character didn't match")

            # if not enemies or ores
            self.press_button("tools", "pickaxe")
            time.sleep(waiting_time)

    def press_button(self, category, item):
        item_image = self.image_dict[category][item]
        _, item_centers, status = self.get_boxes(category, image=item_image)
        if status and len(item_centers) > 0:
            x = item_centers[0][0]
            y = item_centers[0][1]
            self.mouse_controller.click(x, y)
            return True
        else:
            self.logger.warning("Item didn't match: " + item)
            return False

    def measure_time(self, function, *args):
        time1 = time.time()
        function(*args)
        time2 = time.time()
        self.logger.info("Time: " + str(time2 - time1))


if __name__ == "__main__":
    bot = Bot(debug=False)
    bot.start()
    # bot.keep_drawing_boxes("tools")
