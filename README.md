
# HackNRollPBK: Body-Controlled Subway Surfer Game

## Dependencies Installation
For All:

```bash
pip install opencv-python mediapipe pynput pytesseract
```

## Tesseract Installation
### For macOS:
Run the following command in the terminal:
```bash
brew install tesseract
```

### For Windows:
Install Tesseract from the following link:
[Tesseract Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki)

## Quick Setup Guide
1. **Launch Subway Surfer Game**  
   Visit the following link in your browser:
   [Subway Surfers on Poki](https://poki.com/en/g/subway-surfers)

2. **Adjust Screen Ratios**  
   - Fullscreen the game.
   - You will need to adjust the mouse click areas and screenshot regions depending on your screen size. For example, on a 14-inch MacBook:
     - **Mouse Clicks**: The game requires precise mouse clicks, which are affected by your screen resolution. 
     - **Screenshot Area**: The game’s score is displayed in a specific region of the screen. You need to adjust the screenshot region to capture the score accurately.
   
3. **Identify the Coordinates**  
   - Play the game and find the **top-left corner** where the score is displayed once you finish the game.
   - Capture the **pixel** of that corner and use it to calculate the **width** and **height** of the box surrounding the score.

4. **Update Coordinates in `main.py`**  
   Open `main.py` and update the following values based on your screen settings:

```python
CLICK_X_COORINDATE = 890   # Update this value
CLICK_Y_COORINDATE = 850   # Update this value
CLICK_COORINDATES = (CLICK_X_COORINDATE, CLICK_Y_COORINDATE)

SCREENSHOT_X_REGION = 745  # Update this value
SCREENSHOT_Y_REGION = 280  # Update this value
SCREENSHOT_WIDTH = 245     # Update this value
SCREENSHOT_HEIGHT = 42     # Update this value
```

5. **Starting the App**  
   Run the following command to start the app and ensure your score is recorded:
   
   ```bash
   python main.py <room_number> <name>
   ```

   Replace `<room_number>` with your room number and `<name>` with your desired player name.

6. **Positioning Your Face**  
   After starting the app, align your face just below the middle row of the blue top column (near the blue line).

## Controls:
1. **Move Left and Right**: Move your character left and right by tilting your head in the respective directions.
2. **Head at Top Column**: To make your character jump, position your head near the top column.
3. **Head at Bottom Column**: To make your character roll, position your head near the bottom column.
4. **Restart the Game**: After the score screen appears, place your head at the top column for 5 seconds to restart the game.
5. **Check Score**: Squat for 5 seconds to check your current score.

Enjoy playing and have fun competing with your friends!
