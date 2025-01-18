import cv2
import mediapipe as mp
from pynput.keyboard import Controller, Key
from threading import Thread, Lock
import time
from screenshot_click_module import click_and_screenshot
from leaderboard import display_leaderboard
import numpy as np
from screenshot import join_or_create_leaderboard
import sys

if len(sys.argv) != 2:
    print("Pass 2 Argument: 1) Room Id 2) Player Id")

room_id = sys.argv[1]
player_id = sys.argv[2]

# Initialize Mediapipe pose, hands detection, and pynput keyboard controller
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
keyboard = Controller()
frame_lock = Lock()

# Constants for jump/squat regions and lane thresholds
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
lane_thresholds = {
    "left": FRAME_WIDTH * (1 / 3),
    "center": FRAME_WIDTH * (2 / 3),
}
TOP_REGION = FRAME_HEIGHT * 0.2
BOTTOM_REGION = FRAME_HEIGHT * 0.8
COOLDOWN_TIME = 0.3  # Cooldown for key presses in seconds

# Shared variables
frame = None
running = True
last_key_time = time.time()
last_lane = None
thumbs_up_time = 0
thumbs_up_detected = False

# Pre-render leaderboard
def create_leaderboard_image():
    blank = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
    return display_leaderboard(blank)

leaderboard_image = create_leaderboard_image()

# Pre-render static overlay
def create_static_overlay():
    overlay = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
    cv2.line(overlay, (int(lane_thresholds["left"]), 0), 
             (int(lane_thresholds["left"]), FRAME_HEIGHT), (0, 255, 0), 2)
    cv2.line(overlay, (int(lane_thresholds["center"]), 0), 
             (int(lane_thresholds["center"]), FRAME_HEIGHT), (0, 255, 0), 2)
    cv2.line(overlay, (0, int(TOP_REGION)), 
             (FRAME_WIDTH, int(TOP_REGION)), (255, 0, 0), 2)  # Jump region
    cv2.line(overlay, (0, int(BOTTOM_REGION)), 
             (FRAME_WIDTH, int(BOTTOM_REGION)), (255, 0, 0), 2)  # Squat region
    return overlay

static_overlay = create_static_overlay()

# Capture video thread
def capture_video():
    global frame, running
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open the camera.")
        running = False
        return
    while running:
        ret, captured_frame = cap.read()
        if not ret:
            print("Error: Frame not read properly.")
            running = False
            break
        with frame_lock:
            frame = cv2.flip(cv2.resize(captured_frame, (FRAME_WIDTH, FRAME_HEIGHT)), 1)
    cap.release()

video_thread = Thread(target=capture_video)
video_thread.start()

# Main loop
try:
    show_leaderboard = False

    while running:
        # Safely access the shared frame
        with frame_lock:
            if frame is None:
                time.sleep(0.01)
                continue
            displayed_frame = frame.copy()

        # Mediapipe pose and hand processing
        rgb_frame = cv2.cvtColor(displayed_frame, cv2.COLOR_BGR2RGB)
        pose_results = pose.process(rgb_frame)
        hand_results = hands.process(rgb_frame)

        # Draw pose landmarks and handle jump/squat
        if pose_results.pose_landmarks:
            mp_drawing.draw_landmarks(displayed_frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = pose_results.pose_landmarks.landmark
            nose = landmarks[mp_pose.PoseLandmark.NOSE]
            nose_x = int(nose.x * FRAME_WIDTH)
            nose_y = int(nose.y * FRAME_HEIGHT)
            current_time = time.time()

            if nose_y < TOP_REGION and current_time - last_key_time > COOLDOWN_TIME:
                print("Jump detected")
                keyboard.press(Key.up)
                keyboard.release(Key.up)
                last_key_time = current_time

            elif nose_y > BOTTOM_REGION and current_time - last_key_time > COOLDOWN_TIME:
                print("Squat detected")
                keyboard.press(Key.down)
                keyboard.release(Key.down)
                last_key_time = current_time

            # Determine current lane and handle movement
            current_lane = (
                "left" if nose_x < lane_thresholds["left"]
                else "center" if nose_x < lane_thresholds["center"]
                else "right"
            )
            if current_lane != last_lane and current_time - last_key_time > COOLDOWN_TIME:
                if current_lane == "center" and last_lane == "left":
                    print("Move right")
                    keyboard.press(Key.right)
                    keyboard.release(Key.right)
                elif current_lane == "right" and last_lane == "center":
                    print("Move right")
                    keyboard.press(Key.right)
                    keyboard.release(Key.right)
                elif current_lane == "center" and last_lane == "right":
                    print("Move left")
                    keyboard.press(Key.left)
                    keyboard.release(Key.left)
                elif current_lane == "left" and last_lane == "center":
                    print("Move left")
                    keyboard.press(Key.left)
                    keyboard.release(Key.left)
                last_key_time = current_time
                last_lane = current_lane

        # Handle thumbs up gesture for screenshot
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                if thumb_tip.y < index_tip.y:
                    if not thumbs_up_detected:
                        thumbs_up_time = time.time()
                    thumbs_up_detected = True
                else:
                    thumbs_up_detected = False
                    thumbs_up_time = 0

                if thumbs_up_detected and time.time() - thumbs_up_time >= 3:
                    print("Thumbs up held for 3 seconds!")
                    # Invoke the function here (define later)
                    file_path = click_and_screenshot(SCREENSHOT_VARIABLES, CLICK_COORINDATES)
                    join_or_create_leaderboard(player_id, room_id, file_path)
                    thumbs_up_time = 0
                    thumbs_up_detected = False

        # Overlay static elements and leaderboard
        cv2.addWeighted(static_overlay, 1.0, displayed_frame, 1.0, 0, displayed_frame)
        if show_leaderboard:
            alpha = 0.8
            cv2.addWeighted(leaderboard_image, alpha, displayed_frame, 1 - alpha, 0, displayed_frame)

        # Display the frame
        cv2.imshow("Video Feed with Leaderboard", displayed_frame)

        # Key press handling
        key = cv2.waitKey(10) & 0xFF
        if key == ord("w"):
            show_leaderboard = not show_leaderboard
            print(f"Leaderboard display toggled: {show_leaderboard}")
        if key == ord("q"):
            running = False
            break

finally:
    running = False
    video_thread.join()
    cv2.destroyAllWindows()
    pose.close()
    hands.close()
