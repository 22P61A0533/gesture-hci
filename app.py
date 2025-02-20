import streamlit as st
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import os

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Webcam Configuration
FRAME_WIDTH, FRAME_HEIGHT = 640, 480

# Function to Move Mouse Pointer
def move_mouse(index_x, index_y):
    screen_width, screen_height = pyautogui.size()
    mouse_x = np.interp(index_x, (0, FRAME_WIDTH), (0, screen_width))
    mouse_y = np.interp(index_y, (0, FRAME_HEIGHT), (0, screen_height))
    pyautogui.moveTo(mouse_x, mouse_y, duration=0.1)

# Function to Process Video and Control Mouse
def process_video():
    cap = cv2.VideoCapture(0)
    cap.set(3, FRAME_WIDTH)
    cap.set(4, FRAME_HEIGHT)

    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        prev_y = None  # For scroll gesture
        last_gesture_time = time.time()  # To prevent accidental multi-clicks

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            frame = cv2.flip(frame, 1)  # Mirror effect

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Extract Finger Tip Coordinates
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

                    index_x, index_y = int(index_finger_tip.x * FRAME_WIDTH), int(index_finger_tip.y * FRAME_HEIGHT)
                    wrist_y = int(wrist.y * FRAME_HEIGHT)  # Wrist Y Position

                    move_mouse(index_x, index_y)  # Move Cursor

                    # 🖱 *Left Click (Pinch Index & Thumb)*
                    if abs(thumb_tip.x - index_finger_tip.x) < 0.02:
                        if time.time() - last_gesture_time > 0.5:
                            pyautogui.click()
                            last_gesture_time = time.time()

                    # 🔹 *Right Click (Pinch Middle Finger & Thumb)*
                    if abs(thumb_tip.x - middle_finger_tip.x) < 0.02:
                        if time.time() - last_gesture_time > 0.5:
                            pyautogui.rightClick()
                            last_gesture_time = time.time()

                    # 🔄 *Scrolling Gesture (Move Palm Up/Down)*
                    global scroll_enabled
                    if prev_y is not None:
                        if abs(wrist_y - prev_y) > 20:
                            if wrist_y < prev_y:
                                pyautogui.scroll(5)  # Scroll Up
                            else:
                                pyautogui.scroll(-5)  # Scroll Down
                            scroll_enabled = False
                            time.sleep(0.2)  # Small delay

                    prev_y = wrist_y

                    # 📂 *Custom Gesture Commands*
                    if index_x < 50:  # Swipe Left → Open Notepad
                        os.system("notepad.exe")

                    elif index_x > FRAME_WIDTH - 50:  # Swipe Right → Open Calculator
                        os.system("calc.exe")

                    elif abs(thumb_tip.x - index_finger_tip.x) < 0.02 and abs(thumb_tip.x - middle_finger_tip.x) < 0.02:
                        pyautogui.press("volumeup")  # 🔊 Pinch Close → Volume Up

                    elif abs(thumb_tip.y - middle_finger_tip.y) < 0.02 and abs(index_finger_tip.y - middle_finger_tip.y) > 0.05:
                        pyautogui.press("volumedown")  # 🔉 Pinch Open → Volume Down

            cv2.imshow("Gesture Mouse Control", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

# Streamlit UI
def streamlit_ui():
    st.title("🖐 Gesture-Controlled Mouse Interface")
    st.write("Use your hand gestures to control the mouse, scroll, and execute commands.")

    st.subheader("📜 Gesture Controls:")
    st.markdown("""
    1️⃣ *Run the script* and position your *hand in front of the camera*  
    2️⃣ *Move Index Finger* → Moves the *cursor* 🖱  
    3️⃣ *Pinch Index + Thumb* → Left Click 🖱  
    4️⃣ *Pinch Middle Finger + Thumb* → Right Click 🖱  
    5️⃣ *Move Palm Up/Down* → Scroll *Page* 🔄  
    6️⃣ *Swipe Left/Right* → Open *Notepad / Calculator* 📂  
    7️⃣ *Pinch All Fingers Together* → Adjust *Volume* 🔉  
    """)

    st.subheader("📹 Live Gesture Control")
    if st.button("Start Gesture Mouse Control"):
        process_video()

if _name_ == '_main_':
    streamlit_ui()