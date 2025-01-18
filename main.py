import cv2
import mediapipe as mp
import pyautogui
from pynput.keyboard import Controller, Key
from threading import Thread
import time

# Initialize Mediapipe pose and hands detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize pynput keyboard controller
keyboard = Controller()

# Cooldown timer for key presses
last_lane = None
COOLDOWN_TIME = 0.3  # 300ms cooldown
last_key_time = time.time()

# Screen dimensions and lane thresholds
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Regions for jump and squat
TOP_REGION = FRAME_HEIGHT * 0.3  # Top 30% of the screen
BOTTOM_REGION = FRAME_HEIGHT * 0.7  # Bottom 30% of the screen

# Mouse click location and screenshot region
CLICK_LOCATION = (1110, 1000)  # Example (x, y) location for mouse click
SCREENSHOT_REGION = (1056 , 305, 1152, 353)  # Example (x, y, width, height)

# Shared frame storage for multithreading
frame = None
running = True

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

def perform_mouse_action():
    """Perform mouse double-click and take a screenshot."""
    print("Performing mouse action...")
    pyautogui.moveTo(*CLICK_LOCATION)
    pyautogui.click(clicks=2, interval=0.2)  # Double-click
    screenshot = pyautogui.screenshot(region=SCREENSHOT_REGION)
    screenshot.save("screenshot.png")
    print("Screenshot taken and saved as 'screenshot.png'")

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

        # Detect hand signals
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Check for specific hand signal (e.g., thumb up)
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Example condition: Thumb above index finger (thumbs up gesture)
                if thumb_tip.y < index_tip.y:
                    print("Thumbs up detected!")
                    perform_mouse_action()
                    time.sleep(1)  # Prevent repeated detection

                # Draw hand landmarks
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Detect body movements (jump, squat, lane change)
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

            # Draw landmarks and regions on the frame
            mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Display the mirrored frame
        cv2.imshow('Gesture Control with Mediapipe', frame)

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
