import cv2
import mediapipe as mp
from pynput.keyboard import Controller, Key
from threading import Thread
import time

# Initialize Mediapipe pose detection and pynput keyboard controller
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
keyboard = Controller()

# Cooldown timers
action_cooldown = {"up": 0, "down": 0, "left": 0, "right": 0}
COOLDOWN_TIME = 0.5  # 500ms cooldown

# Screen dimensions (divided into regions)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
region_thresholds = {
    "up": FRAME_HEIGHT * 0.3,
    "down": FRAME_HEIGHT * 0.7,
    "left": FRAME_WIDTH * 0.3,
    "right": FRAME_WIDTH * 0.7,
}

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
        frame = cv2.resize(captured_frame, (FRAME_WIDTH, FRAME_HEIGHT))  # Resize for consistent regions
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
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            # Extract landmarks
            landmarks = results.pose_landmarks.landmark
            nose = landmarks[mp_pose.PoseLandmark.NOSE]

            # Map normalized positions to frame dimensions
            nose_x = int(nose.x * FRAME_WIDTH)
            nose_y = int(nose.y * FRAME_HEIGHT)
            current_time = time.time()

            # Determine screen region for the nose position
            if nose_y < region_thresholds["up"] and current_time - action_cooldown["up"] > COOLDOWN_TIME:
                print("Head moved up")
                keyboard.press(Key.up)
                keyboard.release(Key.up)
                action_cooldown["up"] = current_time

            elif nose_y > region_thresholds["down"] and current_time - action_cooldown["down"] > COOLDOWN_TIME:
                print("Head moved down")
                keyboard.press(Key.down)
                keyboard.release(Key.down)
                action_cooldown["down"] = current_time

            elif nose_x < region_thresholds["left"] and current_time - action_cooldown["left"] > COOLDOWN_TIME:
                print("Head moved left")
                keyboard.press(Key.right)
                keyboard.release(Key.right)
                action_cooldown["left"] = current_time

            elif nose_x > region_thresholds["right"] and current_time - action_cooldown["right"] > COOLDOWN_TIME:
                print("Head moved right")
                keyboard.press(Key.left)
                keyboard.release(Key.left)
                action_cooldown["right"] = current_time
            else:
                # No significant movement detected
                pass

            # Draw landmarks and regions on the frame
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            # Draw regions
            cv2.line(frame, (0, int(region_thresholds["up"])), (FRAME_WIDTH, int(region_thresholds["up"])), (0, 255, 0), 2)
            cv2.line(frame, (0, int(region_thresholds["down"])), (FRAME_WIDTH, int(region_thresholds["down"])), (0, 255, 0), 2)
            cv2.line(frame, (int(region_thresholds["left"]), 0), (int(region_thresholds["left"]), FRAME_HEIGHT), (255, 0, 0), 2)
            cv2.line(frame, (int(region_thresholds["right"]), 0), (int(region_thresholds["right"]), FRAME_HEIGHT), (255, 0, 0), 2)

        # Display the frame
        cv2.imshow('Head Movement Detection', frame)

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
