"""
Gesture Controlled Video Player using Raspberry Pi and MediaPipe - Play, Pause and Control Volume using Gestures

https://microkontroller.ru/raspberry-pi-projects/upravlyaemyj-zhestami-videopleer-na-raspberry-pi-i-mediapipe/
"""

import cv2 as cv
import mediapipe as mp
import pyautogui as gui
import sys


USE_WEBCAM = (len(sys.argv) > 1) and (sys.argv[1] == "WEBCAM")

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

tipIds = (4, 8, 12, 16, 20)
state = None
Gesture = None
wCam, hCam = 720, 640


def finger_position(image, handNo=0):
    lmList = []
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            # print(id,lm)
            h, w, c = image.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])
    return lmList


if USE_WEBCAM:
    # For webcam input:
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, wCam)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, hCam)

with mp_hands.Hands(
        min_detection_confidence=0.8,
        min_tracking_confidence=0.5) as hands:
    while True if not USE_WEBCAM else cap.isOpened():
        success, image = (True, cv.imread("hand.png")) if not USE_WEBCAM else cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue
        # flip the image horizontally for a later selfie-view display, and convert BGR to RGB
        image = cv.cvtColor(cv.flip(image, 1), cv.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        # draw an annotation for gesture control in the picture
        image.flags.writeable = True
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        lmList = finger_position(image)
        # print(lmList)
        if len(lmList) != 0:
            fingers = []
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    # state = "Play"
                    fingers.append(1)
                if (lmList[tipIds[id]][2] > lmList[tipIds[id] - 2][2]):
                    # state = "Pause"
                    # gui.press('space')
                    # print("Space")
                    fingers.append(0)
            totalFingers = fingers.count(1)
            print(totalFingers)
            # print(lmList[9][2])

            if totalFingers == 4:
                state = "Play"
                # fingers.append(1)
            if totalFingers == 0 and state == "Play":
                state = "Pause"
                gui.press('space')
                print("Space")
            if totalFingers == 1:
                if lmList[8][1] < 300:
                    print("left")
                    gui.press('left')
                if lmList[8][1] > 400:
                    print("Right")
                    gui.press('Right')
            if totalFingers == 2:
                if lmList[9][2] < 210:
                    print("Up")
                    gui.press('Up')
                if lmList[9][2] > 230:
                    print("Down")
                    gui.press('Down')
        # cv.putText(image, str("Gesture"), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv.imshow("Media Controller", image)
        key = cv.waitKey(1) & 0xFF
        if key == 27:
            break

    if USE_WEBCAM:
        cap.release()
    cv.destroyAllWindows()
