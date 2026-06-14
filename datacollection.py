import cv2  #install cvzone opencv mediapipe
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)

offset = 20
imgSize = 300

#folder = "collecteddata/a"
counter = 0

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)
    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']

        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
        imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]

        imgCropShape = imgCrop.shape

        aspectRatio = h / w

        if aspectRatio > 1:
            k = imgSize / h
            wCal = math.ceil(k * w)
            imgResize = cv2.resize(imgCrop, (wCal, imgSize))
            imgResizeShape = imgResize.shape
            wGap = math.ceil((imgSize - wCal) / 2)
            imgWhite[:, wGap:wCal + wGap] = imgResize

        else:
            k = imgSize / w
            hCal = math.ceil(k * h)
            imgResize = cv2.resize(imgCrop, (imgSize, hCal))
            imgResizeShape = imgResize.shape
            hGap = math.ceil((imgSize - hCal) / 2)
            imgWhite[hGap:hCal + hGap, :] = imgResize

        cv2.imshow("ImageCrop", imgCrop)
        cv2.imshow("ImageWhite", imgWhite)

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord("a"):
        folder = "collecteddata/a"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("b"):
        folder = "collecteddata/b"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("c"):
        folder = "collecteddata/c"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("d"):
        folder = "collecteddata/d"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("e"):
        folder = "collecteddata/e"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("f"):
        folder = "collecteddata/f"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("g"):
        folder = "collecteddata/g"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("h"):
        folder = "collecteddata/h"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("i"):
        folder = "collecteddata/i"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("j"):
        folder = "collecteddata/j"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("k"):
        folder = "collecteddata/k"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("l"):
        folder = "collecteddata/l"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("m"):
        folder = "collecteddata/m"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("n"):
        folder = "collecteddata/n"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("o"):
        folder = "collecteddata/o"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("p"):
        folder = "collecteddata/p"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("q"):
        folder = "collecteddata/q"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("r"):
        folder = "collecteddata/r"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("s"):
        folder = "collecteddata/s"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("t"):
        folder = "collecteddata/t"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("u"):
        folder = "collecteddata/u"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("v"):
        folder = "collecteddata/v"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("w"):
        folder = "collecteddata/w"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("x"):
        folder = "collecteddata/x"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("y"):
        folder = "collecteddata/y"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)

    if key == ord("z"):
        folder = "collecteddata/z"
        counter += 1
        gray_image = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', gray_image)
        print(counter)