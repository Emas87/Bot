import os
import cv2
import numpy as np
import wx
import time


class Finder:
    def __init__(self):
        self.base = 'images/test1.png'
        self.templates = ['images/red_gem_left.png']
        self.debug = False
        self.centers = []
        self.rectangles = []

    def find_images(self):
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

    def draw_rentangles(self):
        app = wx.App()
        dc = wx.ScreenDC()
        dc.StartDrawingOnTop(None)
        dc.SetPen(wx.Pen('red', 2))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        for rectangle in self.rectangles:
            boxwidth = rectangle[1]
            boxheight = rectangle[2]
            x = rectangle[0][0]
            y = rectangle[0][1]
            dc.DrawRectangle(x, y, boxwidth, boxheight)
            time.sleep(0.5)
            dc.Clear()


if __name__ == "__main__":
    finder = Finder()
    templates = [os.path.abspath(os.path.join('images', 'Mining', path)) for path in os.listdir('images/Mining')]
    finder.templates = templates
    files = [os.path.abspath(os.path.join('images', path)) for path in os.listdir('images')]
    finder.debug = True
    for test_file in files:
        if "test" in test_file:
            finder.base = test_file
            finder.find_images()
            finder.draw_rentangles()

