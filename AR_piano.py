"""
AR piano.
"""

from cvzone.HandTrackingModule import HandDetector
import cv2
import pyautogui as gui
import math
from dataclasses import dataclass
from cv2.typing import MatLike


KEYS = (
    ('z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'),
    ('a',  '', 'd', 'f',  '', 'h', 'j', 'k',  '', ';', '\'')
)


@dataclass
class Button:
    pos: list
    text: str
    size: list
    color: tuple


def create_keyboard() -> list[Button]:
    buttonList = []
    for i in range(len(KEYS)):
        for j, key in enumerate(KEYS[i]):   
            if i == 0:
                buttonList.append(Button([38*j+15,0], key, [35,100], (255,255,255)))
            elif key != '':
                buttonList.append(Button([38*(j-1)+15+35//6*5,0], key, [35//3*2,50], (0,0,0)))
    return buttonList


def draw_keyboard(img: MatLike, buttonList: list[Button]) -> MatLike:
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        colour = button.color
        cv2.rectangle(img, button.pos, (x+w,y+h), colour, cv2.FILLED)
        cv2.circle(img, (x+w//2,y+h//3*2), 10, (255, 0, 0), cv2.FILLED)
        cv2.putText(img, button.text, (x+10,y+h-10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (214,0,220), 2)
    return img


def find_distance(p1: list, p2: list) -> float:
    x1, y1 = p1
    x2, y2 = p2
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    length = math.hypot(x2 - x1, y2 - y1)
    return length


buttonList = create_keyboard()

# Initialize the webcam to capture video
# The '2' indicates the third camera connected to your computer; '0' would usually refer to the built-in camera
cap = cv2.VideoCapture(0)

# Initialize the HandDetector class with the given parameters
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)

# Continuously get frames from the webcam
while cap.isOpened():
    # Capture each frame from the webcam
    # 'success' will be True if the frame is successfully captured, 'img' will contain the frame
    success, img = cap.read()
    img = cv2.resize(img, (1024, 576))
    img = cv2.flip(img, 1)

    # Find hands in the current frame
    # The 'draw' parameter draws landmarks and hand outlines on the image if set to True
    # The 'flipType' parameter flips the image, making it easier for some detections
    hands, img = detector.findHands(img, draw=True, flipType=False)
    img = draw_keyboard(img, buttonList)

    # Check if any hands are detected
    if hands:
        # Information for the first hand detected
        hand1 = hands[0]  # Get the first hand detected
        lmList1 = hand1["lmList"]  # List of 21 landmarks for the first hand
        bbox1 = hand1["bbox"]  # Bounding box around the first hand (x,y,w,h coordinates)
        center1 = hand1['center']  # Center coordinates of the first hand
        handType1 = hand1["type"]  # Type of the first hand ("Left" or "Right")
        #cv2.circle(img, lmList1[8][0:2], 15, (255, 0, 0), 2)  # draw a dot on the tip of the index finger

        # Calculate distance between specific landmarks on the first hand and draw it on the image
        #length, info, img = detector.findDistance(lmList1[8][0:2], lmList1[12][0:2], img, color=(255, 0, 255), scale=10)
        for button in buttonList:
            x, y = button.pos
            w, h = button.size
            p = (x+w//2, y+h//3*2)
            if find_distance(lmList1[8][0:2], p) < 20:
                cv2.rectangle(img, button.pos, (x+w,y+h), (0,0,255), cv2.FILLED)

        # Check if a second hand is detected
        if len(hands) == 2:
            # Information for the second hand
            hand2 = hands[1]
            lmList2 = hand2["lmList"]
            bbox2 = hand2["bbox"]
            center2 = hand2['center']
            handType2 = hand2["type"]

            # Calculate distance between the index fingers of both hands and draw it on the image
            #length, info, img = detector.findDistance(lmList1[8][0:2], lmList2[8][0:2], img, color=(255, 0, 0), scale=10)

        #print(" ")  # New line for better readability of the printed output

    # Display the image in a window
    cv2.imshow("Image", img)

    # Keep the window open and update it for each frame; wait for 1 millisecond between frames
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    elif 32 < key < 128:
        sym = chr(key)
        print(sym, key)
        gui.press(sym)

cap.release()
cv2.destroyAllWindows()
