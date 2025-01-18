import firebase_admin
from firebase_admin import credentials, firestore
import os
import pytesseract
from PIL import Image
import pyautogui

# Initialize Firebase Admin SDK
cred = credentials.Certificate("./firebase_config.json")
firebase_admin.initialize_app(cred)

# Access Firestore
db = firestore.client()
image_path = "./image.jpg"
player_id = 3
room_id = 1

# Function to process the screenshot and extract number
def extract_number_from_image(image_path):
    pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"  # Update if necessary
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, config="--psm 7")  # PSM 7 assumes a single line of text
    print(f"Extracted text: {text}")
    
    # Extract numeric data
    number = "".join(filter(str.isdigit, text))
    if number:
        print(f"Extracted number: {number}")
        return int(number)
    else:
        print("No number detected.")
        return None

# Function to create or join a private leaderboard
def join_or_create_leaderboard(player_id, room_id):
    score = extract_number_from_image(image_path)
    if score is None:
        print("No valid score extracted from the image. Exiting.")
        return
    
    collection_name = f"private_{room_id}"
    private_leaderboard_id = f"private_{player_id}"
    
    leaderboard_ref = db.collection(collection_name).document(private_leaderboard_id)

    # Check if the leaderboard exists
    doc = leaderboard_ref.get()
    print(doc.exists)
    if doc.exists:
        print(f"Joining existing leaderboard for {player_id}")

        leaderboard_data = doc.to_dict()  # Get the data from the document
        existing_score = leaderboard_data.get('scores', None)

        if existing_score is not None:
            # Extract the existing score
            
            # If the new score is higher, update it
            if score > existing_score:
                print(f"New score {score} is higher than existing score {existing_score}. Updating score.")
                
                # Remove the old score and add the new one
                leaderboard_ref.update({
                    "scores": score  # Remove the old score
                })
                
            else:
                print(f"New score {score} is not higher than existing score {existing_score}. No update needed.")
        else:
            # If the player doesn't have a score, add the new score
            print(f"Player {player_id} not found in leaderboard. Adding new score.")
            leaderboard_ref.update({
                "scores": score  # Add new score
            })
    else:
        # If the leaderboard doesn't exist, create it
        print(f"Creating new leaderboard for {player_id}")
        leaderboard_ref.set({
            "scores": score  # Ensure this is a list of dictionaries
        })

# Extract the number and update the leaderboard
extract_number_from_image(image_path)
join_or_create_leaderboard(player_id, room_id)
