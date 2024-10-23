import cv2


def show_webcam(mirror=False):
    n = 0
# use the device /dev/video{n} in this case /dev/video0
# On windows use the first connected camera in the device tree
    cam = cv2.VideoCapture(n)
    while True:
# read what the camera the images which are comming from the camera
# ret_val idk atm
        ret_val, img = cam.read()
# if mirror is true do flip the image
        if mirror:
            img = cv2.flip(img, 1)
# show the image with the title my webcam in a window
        cv2.imshow('my webcam', img)
# if you press ESC break out of the while loop and destroy all windows == free resources <3
        if cv2.waitKey(1) == 27:
            break  # esc to quit
    cv2.destroyAllWindows()


def main():
    show_webcam(mirror=True)


if __name__ == '__main__':
    main()