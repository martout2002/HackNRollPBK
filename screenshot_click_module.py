import os
import pyautogui

def ensure_directory(directory_path):
    """Ensure the directory exists, create if it does not."""
    os.makedirs(directory_path, exist_ok=True)

def take_screenshot(file_path, region):
    """
    Takes a screenshot of a specified region and saves it to the given file path.

    Parameters:
        file_path (str): The path where the screenshot will be saved.
        region (tuple): A tuple specifying the screenshot region (x, y, width, height).
    """
    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    ensure_directory(directory)

    # Take the screenshot
    pyautogui.screenshot(file_path, region=region)
    print(f"Screenshot saved to {file_path}")

def click_and_screenshot(region, click_point=None):
    """
    Simulates a click and takes a screenshot of a specified region.

    Parameters:
        region (tuple): A tuple specifying the screenshot region (x, y, width, height).
        click_point (tuple): Optional tuple specifying the point to click (x, y).

    Returns:
        str: The file path where the screenshot is saved.
    """
    # Ensure the images directory exists
    images_dir = "images"
    ensure_directory(images_dir)

    # Generate a unique file name
    file_path = os.path.join(images_dir, "screenshot.png")

    # Determine the click point
    if click_point is None:
        # Default to the center of the region if no click_point is provided
        click_x = region[0] + region[2] // 2
        click_y = region[1] + region[3] // 2
    else:
        click_x, click_y = click_point

    # Simulate a click
    pyautogui.click(click_x, click_y)
    pyautogui.click(click_x, click_y)
    print(f"Clicked at ({click_x}, {click_y})")

    # Take the screenshot
    take_screenshot(file_path, region)

    # Return the file path
    return file_path
