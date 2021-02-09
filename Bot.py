import cv2
import os


def find_images(base='images/test.png', images=['images/red_gem_left.png']):
    method = cv2.TM_SQDIFF_NORMED

    # Read the base images
    base_cv = cv2.imread(base)

    # look for images
    results = []
    for image in images:
        small_image = cv2.imread(image)
        result = cv2.matchTemplate(small_image, base_cv, method)

        # We want the minimum squared difference
        mn, _, mnloc, _ = cv2.minMaxLoc(result)

        # Draw the rectangle:
        # Extract the coordinates of our best match
        mpx, mpy = mnloc

        if mn > 0.1:
            continue
        # Step 2: Get the size of the template. This is the same size as the match.
        trows, tcols = small_image.shape[:2]

        # Step 3: Draw the rectangle on large_image
        cv2.rectangle(base_cv, (mpx, mpy), (mpx+tcols, mpy+trows), (0, 0, 255), 2)

    # Display the original image with the rectangle around the match.
    cv2.imshow('output', base_cv)

    # The image is only displayed if we call this
    cv2.waitKey(0)


if __name__ == "__main__":
    tests = [os.path.abspath(os.path.join('images', 'Mining', path)) for path in os.listdir('images/Mining')]
    find_images(images=tests)
