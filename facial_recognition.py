import cv2
import numpy as np
import face_recognition
from pathlib import Path
from io import BytesIO
import logging

# Set up detailed configuration for logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

FACES_DIR = Path("data/registered_faces")
if not FACES_DIR.exists():
    FACES_DIR.mkdir(parents=True, exist_ok=True)

def register_face(image_data, first_name, last_name):
    try:
        image = face_recognition.load_image_file(BytesIO(image_data))
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            file_path = FACES_DIR / f"{first_name}_{last_name}_embedding.npy"
            np.save(file_path, face_encodings[0])  
            return {"success": True, "audio": "/static/audio/Successfully registered f 1.wav"}  # Success audio
        else:
            return {"success": False, "audio": "/static/audio/alr_reg.wav"}  # Failure audio (no face found)
    except Exception as e:
        return {"success": False, "audio": "/static/audio/Registering new faces th 1.wav"}  # General error audio



def authenticate_face(image_data):
    try:
        image_to_check = face_recognition.load_image_file(BytesIO(image_data))
        encoding_to_check = face_recognition.face_encodings(image_to_check)

        if encoding_to_check:
            encoding_to_check = encoding_to_check[0]
            known_face_encodings = []
            known_face_names = []

            # Load all registered face encodings and names
            for file in FACES_DIR.glob("*.npy"):
                known_face_encodings.append(np.load(file))
                known_face_names.append(file.stem.replace("_embedding", ""))

            # Compute distances between known face encodings and the uploaded encoding
            distances = face_recognition.face_distance(known_face_encodings, encoding_to_check)
            best_match_index = np.argmin(distances)

            # Set a stricter threshold for face matching (e.g., 0.4 is more strict than 0.6)
            if distances[best_match_index] < 0.4:  # Lowering threshold for stricter matching
                response_message = f"Authentication successful for {known_face_names[best_match_index]} with distance {distances[best_match_index]:.2f}."
                logging.info(response_message)
                return {
                    "message": "Authentication successful", 
                    "user": known_face_names[best_match_index], 
                    "audio": "/static/audio/Authentication Successful 2.wav"
                }
            else:
                # If no match is found, return failure with appropriate audio
                response_message = f"No matching face found. Closest distance: {distances[best_match_index]:.2f}."
                logging.info(response_message)
                return {
                    "message": "Authentication failed",
                    "audio": "/static/audio/Access Denied I was not 1.wav"
                }
        else:
            # If no faces are detected in the image, return failure with appropriate audio
            response_message = "No faces detected in the image."
            logging.warning(response_message)
            return {
                "message": "No face detected",
                "audio": "/static/audio/It seems no face or multi 1.wav"
            }
    except Exception as e:
        logging.error(f"Error during authentication: {e}")
        return {
            "message": "Error during authentication",
            "audio": "/static/audio/Access Denied Insufficie 1.wav"
        }
