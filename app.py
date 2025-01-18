import cv2
import pyautogui

# Initialize variables
previous_column = None

# Function to detect humans
def detect_humans(frame, hog):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    boxes, _ = hog.detectMultiScale(gray, winStride=(8, 8), padding=(8, 8), scale=1.05)
    return boxes

# Function to determine movement based on column
def determine_movement(previous_column, current_column):
    if previous_column is None:
        return None  # No movement if no previous column

    if current_column > previous_column:
        return "right"  # Moved right
    elif current_column < previous_column:
        return "left"  # Moved left
    return None  # No movement if still in the same column

# Main video loop
cap = cv2.VideoCapture(0)  # Open camera
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect humans
    boxes = detect_humans(frame, hog)
    if len(boxes) > 0:
        # Assume only one person is detected (use the first box)
        x, y, w, h = boxes[0]
        center_x = x + w // 2
        center_y = y + h // 2

        # Determine the current column
        height, width, _ = frame.shape
        section_width = width // 3
        section_height = height // 3
        current_column = center_x // section_width
        current_row = center_y // section_height

        # Determine movement based on columns
        movement = determine_movement(previous_column, current_column)
        if movement == "left":
            pyautogui.press("left")
        elif movement == "right":
            pyautogui.press("right")

        # Add logic for jumping and ducking
        if current_row == 0:  # Top section
            pyautogui.press("up")  # Jump
        elif current_row == 2:  # Bottom section
            pyautogui.press("down")  # Duck

        # Update previous column
        previous_column = current_column

        # Visualise detection
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Show the frame
    cv2.imshow("Frame", frame)

    # Quit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
