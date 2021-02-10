import os
import cv2
import numpy as np
import wx
import time


class Finder:
    def __init__(self, input_templates=('images/red_gem_left.png',), base='images/test1.png', debug=False):
        self.templates_cv = []
        self.base = base
        self.base_cv_rgb = cv2.imread(self.base)
        self.templates = input_templates
        self.debug = debug
        self.centers = []
        self.rectangles = []

    def find_images_path(self):
        # Resetting cetners and rectangles
        self.centers = []
        self.rectangles = []

        # Setting method
        method = cv2.TM_CCOEFF_NORMED

        # Read the base images and turning it to gray scale
        base_cv_rgb = cv2.imread(self.base)
        if self.debug:
            print(self.base)
        gray = cv2.cvtColor(base_cv_rgb, cv2.COLOR_BGR2GRAY)

        threshold = 0.8

        # look for images
        for image in self.templates:

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
                self.rectangles.append((point, width, height))
                # Store centers of rectangles
                self.centers.append((point[0] + width / 2, point[1] + height / 2))
                if self.debug:
                    cv2.rectangle(base_cv_rgb, point, (point[0] + width, point[1] + height), (0, 0, 255), 2)

        # Display the original image with the rectangle around the match for testing purposes.
        if self.debug:
            cv2.imshow('output', base_cv_rgb)

        # The image is only displayed if we call this, for testing purposes.
        if self.debug:
            cv2.waitKey(0)

    def find_images(self, offset=(0, 0)):
        # Resetting cetners and rectangles
        self.centers = []
        self.rectangles = []

        # Setting method
        method = cv2.TM_CCOEFF_NORMED

        # Read the base images and turning it to gray scale
        gray = cv2.cvtColor(self.base_cv_rgb, cv2.COLOR_BGR2GRAY)

        threshold = 0.8

        # look for images
        rectangles = []
        for image in self.templates_cv:

            # read image to look for
            template = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Step 2: Get the size of the template. This is the same size as the match.
            height, width = template.shape[:2]

            # look for several matches
            result = cv2.matchTemplate(gray, template, method)

            # get locations of all omages above threshold
            loc = np.where(result >= threshold)

            # Draw rectangles frop each location
            for point in zip(*loc[::-1]):
                # top-left, width, height
                rectangles.append((point[0] + offset[0], point[1] + offset[1], width, height))
                # Store centers of rectangles
                self.centers.append((point[0] + offset[0] + width / 2, point[1] + offset[1] + height / 2))
                if self.debug:
                    cv2.rectangle(self.base_cv_rgb, point, (point[0] + offset[0] + width / 2, point[1] + offset[1] +
                                                            height / 2), (0, 0, 255), 2)

        # Display the original image with the rectangle around the match for testing purposes.
        if self.debug:
            cv2.imshow('output', self.base_cv_rgb)

        # The image is only displayed if we call this, for testing purposes.
        if self.debug:
            cv2.waitKey(0)

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
            self.rectangles.append(rectangles[i])

    def draw_rentangles(self):
        print(len(self.rectangles))
        app = wx.App()
        dc = wx.ScreenDC()
        dc.StartDrawingOnTop(None)
        dc.SetPen(wx.Pen('red', 2))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangleList(self.rectangles)
        # for rectangle in self.rectangles:
        #    dc.DrawRectangle(rectangle)

    def load_templates(self):
        for image_path in self.templates:
            template = cv2.imread(image_path)
            self.templates_cv.append(template)

    def load_base_image(self):
        self.base_cv_rgb = cv2.imread(self.base)


if __name__ == "__main__":
    finder = Finder()
    templates = [os.path.abspath(os.path.join('images', 'Mining', path)) for path in os.listdir('images/Mining')]
    finder.templates = templates
    files = [os.path.abspath(os.path.join('images', path)) for path in os.listdir('images')]
    finder.debug = True
    for test_file in files:
        if "test" in test_file:
            finder.base = test_file
            finder.find_images_path()
            finder.draw_rentangles()

