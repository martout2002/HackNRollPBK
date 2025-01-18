import cv2
from screenshot import fetch_leaderboard_data

def display_leaderboard(frame, room_id):
    """Display a leaderboard directly on the OpenCV frame."""
    leaderboard = fetch_leaderboard_data(room_id)
    if not leaderboard:
        leaderboard = ["No data available"]
    y_offset = 50
    for line in leaderboard:
        cv2.putText(
            frame, line, (50, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
        )
        y_offset += 30
    return frame