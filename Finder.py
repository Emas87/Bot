import logging
import os
import cv2
import numpy as np
import wx

import time
class Finder:
    def __init__(self, debug=False):
        self.logger = logging.getLogger(__name__)
        self.base = 'images/test1.png'
        self.templates = ('images/red_gem_left.png',)
        self.debug = debug

    def find_images_path(self, base, templates_i, threshold=0.9):
        # Resetting cetners and rectangles
        centers = []
        rectangles = []

        # Setting method
        method = cv2.TM_CCOEFF_NORMED

        # Read the base images and turning it to gray scale
        base_cv_rgb = cv2.imread(base)
        self.logger.debug(base)
        gray = cv2.cvtColor(base_cv_rgb, cv2.COLOR_BGR2GRAY)

        threshold = 0.8

        # look for images
        for image in templates_i:

            # read image to look for
            template = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

            # Step 2: Get the size of the template. This is the same size as the match.
            height, width = template.shape[:2]

            # look for several matches
            result = cv2.matchTemplate(gray, template, method)

            # get locations of all omages above threshold
            loc = np.where(result >= threshold)

            # Draw rectangles frop each location
            for point in zip(*loc[::-1]):
                # top-left, width, height
                rectangles.append((point, width, height))
                # Store centers of rectangles
                centers.append((point[0] + int(width / 2), point[1] + int(height / 2)))
                if self.debug:
                    cv2.rectangle(base_cv_rgb, point, (point[0] + width, point[1] + height), (0, 0, 255), 2)

        # Display the original image with the rectangle around the match for testing purposes.
        if self.debug:
            cv2.imshow('output', base_cv_rgb)

        # The image is only displayed if we call this, for testing purposes.
        if self.debug:
            cv2.waitKey(0)

        return rectangles, centers, True

    def find_images(self, base_cv_rgb, templates_cv, offset=(0, 0), threshold=0.85):

        # Setting method
        method = cv2.TM_CCOEFF_NORMED

        # Read the base images and turning it to gray scale
        gray = cv2.cvtColor(base_cv_rgb, cv2.COLOR_BGR2GRAY)

        # look for images
        rectangles = []
        centers = []
        for image in templates_cv:

            # read image to look for
            template = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Step 2: Get the size of the template. This is the same size as the match.
            height, width = template.shape[:2]

            # look for several matches
            try:
                result = cv2.matchTemplate(gray, template, method)
            except cv2.error:
                self.logger.error("Something went wrong with matchTemplate using template number: " +
                                  str(templates_cv.index(image)))
                return 0, 0, False

            # get locations of all omages above threshold
            loc = np.where(result >= threshold)

            # Draw rectangles frop each location
            for point in zip(*loc[::-1]):
                # top-left, width, height
                rectangles.append((point[0] + offset[0], point[1] + offset[1], width, height))
                # Store centers of rectangles
                centers.append((point[0] + offset[0] + int(width / 2), point[1] + offset[1] + int(height / 2)))
                if self.debug:
                    start_point = (point[0] + offset[0], point[1] + offset[1])
                    end_point = (point[0] + offset[0] + int(width / 2), point[1] + offset[1] + int(height / 2))
                    color = (0, 0, 255)
                    thickness = 2
                    cv2.rectangle(base_cv_rgb, start_point, end_point, color, thickness)

                    # Display the original image with the rectangle around the match for testing purposes.
        if self.debug:
            cv2.imshow('output', base_cv_rgb)

        # The image is only displayed if we call this, for testing purposes.
        if self.debug:
            cv2.waitKey(0)

        final_rectangles = []
        final_centers = []

        # delete repeated rectangles
        for i in range(0, len(rectangles)):
            matches = 0
            for j in range(0, len(rectangles)):
                matches = 0
                if i < j:
                    for k in range(0, len(rectangles[i])):
                        if abs(rectangles[i][k] - rectangles[j][k]) <= 10:
                            matches += 1
                    if matches == 4:
                        break
            if matches == 4:
                continue
            final_rectangles.append(rectangles[i])
            final_centers.append(centers[i])

        final_rectangles = sorted(final_rectangles)
        final_centers = sorted(final_centers)

        return final_rectangles, final_centers, True

    def draw_rentangles(self, rectangles):
        self.logger.debug(len(rectangles))
        app = wx.App()
        dc = wx.ScreenDC()
        dc.StartDrawingOnTop(None)
        dc.SetPen(wx.Pen('red', 2))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        #dc.DrawRectangleList(rectangles)
        for rectangle in rectangles:
            dc.DrawRectangle(rectangle)
            time.sleep(0.05)
            dc.DrawRectangle(rectangle)

    @staticmethod
    def load_image(image_path):
            return cv2.imread(image_path)


if __name__ == "__main__":
    finder = Finder()
    templates = [os.path.abspath(os.path.join('images', 'Mining', path)) for path in os.listdir('images/Mining')]
    files = [os.path.abspath(os.path.join('images', path)) for path in os.listdir('images')]
    finder.debug = True
    for test_file in files:
        if "test" in test_file:
            base = test_file
            finder.find_images_path(base, templates)
            finder.draw_rentangles()
