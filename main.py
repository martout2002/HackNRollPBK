import cv2
import mediapipe as mp
from pynput.keyboard import Controller, Key
from threading import Thread
import time
from screenshot_click_module import click_and_screenshot
from screenshot import join_or_create_leaderboard
import sys

if len(sys.argv) != 2:
    print("Pass 2 Argument: 1) Room Id 2) Player Id")

room_id = sys.argv[1]
player_id = sys.argv[2]


# Initialize Mediapipe pose and hand detection, and pynput keyboard controller
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
keyboard = Controller()

# Cooldown timer for key presses
last_lane = None
COOLDOWN_TIME = 0.3  # 300ms cooldown
last_key_time = time.time()

# Screen dimensions and lane thresholds
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
lane_thresholds = {
    "left": FRAME_WIDTH * (1 / 3),  # Left lane end
    "center": FRAME_WIDTH * (2 / 3),  # Center lane end
}

CLICK_X_COORINDATE = 1110
CLICK_Y_COORINDATE = 1000
CLICK_COORINDATES = (CLICK_X_COORINDATE, CLICK_Y_COORINDATE)

SCREENSHOT_X_REGION = 945
SCREENSHOT_Y_REGION = 302
SCREENSHOT_WIDTH = 309
SCREENSHOT_HEIGHT = 51
SCREENSHOT_VARIABLES = (SCREENSHOT_X_REGION, SCREENSHOT_Y_REGION, SCREENSHOT_WIDTH, SCREENSHOT_HEIGHT)

# Regions for jump and squat
TOP_REGION = FRAME_HEIGHT * 0.2  # Top 20% of the screen
BOTTOM_REGION = FRAME_HEIGHT * 0.8  # Bottom 20% of the screen

# Shared frame storage for multithreading
frame = None
running = True

# Thumbs up detection state
thumbs_up_time = 0
thumbs_up_detected = False

def capture_video():
    """Thread to capture video frames."""
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
        # Resize and mirror the frame
        captured_frame = cv2.resize(captured_frame, (FRAME_WIDTH, FRAME_HEIGHT))
        frame = cv2.flip(captured_frame, 1)  # Mirror the frame horizontally
    cap.release()

# Start video capture thread
video_thread = Thread(target=capture_video)
video_thread.start()

try:
    while running:
        if frame is None:
            time.sleep(0.01)  # Wait for the first frame
            continue

        # Convert frame to RGB for Mediapipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = pose.process(rgb_frame)
        hand_results = hands.process(rgb_frame)

        if pose_results.pose_landmarks:
            # Extract landmarks
            landmarks = pose_results.pose_landmarks.landmark
            nose = landmarks[mp_pose.PoseLandmark.NOSE]

            # Map normalized nose position to frame dimensions
            nose_x = int(nose.x * FRAME_WIDTH)
            nose_y = int(nose.y * FRAME_HEIGHT)

            current_time = time.time()

            # Detect jump and squat based on nose position in the frame
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

            # Determine current lane
            if nose_x < lane_thresholds["left"]:
                current_lane = "left"
            elif nose_x < lane_thresholds["center"]:
                current_lane = "center"
            else:
                current_lane = "right"

            # Handle lane change if cooldown has elapsed
            if current_lane != last_lane and current_time - last_key_time > COOLDOWN_TIME:
                if last_lane == "left" and current_lane == "center":
                    print("Move right")
                    keyboard.press(Key.right)
                    keyboard.release(Key.right)
                elif last_lane == "center":
                    if current_lane == "right":
                        print("Move right")
                        keyboard.press(Key.right)
                        keyboard.release(Key.right)
                    elif current_lane == "left":
                        print("Move left")
                        keyboard.press(Key.left)
                        keyboard.release(Key.left)
                elif last_lane == "right" and current_lane == "center":
                    print("Move left")
                    keyboard.press(Key.left)
                    keyboard.release(Key.left)

                last_key_time = current_time
                last_lane = current_lane

            # Draw landmarks, lanes, and regions on the frame
            mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Draw lane boundaries
            cv2.line(frame, (int(lane_thresholds["left"]), 0), (int(lane_thresholds["left"]), FRAME_HEIGHT), (0, 255, 0), 2)
            cv2.line(frame, (int(lane_thresholds["center"]), 0), (int(lane_thresholds["center"]), FRAME_HEIGHT), (0, 255, 0), 2)

            # Draw jump/squat regions
            cv2.line(frame, (0, int(TOP_REGION)), (FRAME_WIDTH, int(TOP_REGION)), (255, 0, 0), 2)  # Top region
            cv2.line(frame, (0, int(BOTTOM_REGION)), (FRAME_WIDTH, int(BOTTOM_REGION)), (255, 0, 0), 2)  # Bottom region

            # Draw current nose position
            cv2.circle(frame, (nose_x, nose_y), 5, (0, 0, 255), -1)  # Current position

        # Detect hand signals (thumbs up)
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Thumb tip and index finger tip coordinates
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Calculate relative position (thumb above index finger)
                if thumb_tip.y < index_tip.y:  # Thumbs up condition
                    print("Thumbs up detected!")
                    if not thumbs_up_detected:
                        thumbs_up_time = time.time()
                    thumbs_up_detected = True
                else:
                    thumbs_up_detected = False
                    thumbs_up_time = 0  # Reset the thumbs up timer

                # Check if thumbs up has been held for 3 seconds
                if thumbs_up_detected and time.time() - thumbs_up_time >= 3:
                    print("Thumbs up held for 3 seconds!")
                    # Invoke the function here (define later)
                    file_path = click_and_screenshot(SCREENSHOT_VARIABLES, CLICK_COORINDATES)
                    join_or_create_leaderboard(player_id, room_id, file_path)
                    
                    thumbs_up_detected = False
                    thumbs_up_time = 0  # Reset the timer after invoking the function

                # Draw hand landmarks 
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Display the mirrored frame
        cv2.imshow('Subway Surfer Lane Control (Mirrored)', frame)

        # Break loop on 'q' key
        if cv2.waitKey(10) & 0xFF == ord('q'):
            running = False
            break
finally:
    # Clean up
    running = False
    video_thread.join()
    cv2.destroyAllWindows()
    pose.close()
    hands.close()
