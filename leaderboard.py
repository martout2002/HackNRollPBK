import cv2

def display_leaderboard(frame):
    """Display a leaderboard directly on the OpenCV frame."""
    leaderboard = [
        "Private Leaderboard",
        "1. Player1 - 999999 points",
        "2. Player2 - 888888 points",
        "3. Player3 - 777777 points",
    ]
    y_offset = 50
    for line in leaderboard:
        cv2.putText(
            frame, line, (50, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
        )
        y_offset += 30
    return frame