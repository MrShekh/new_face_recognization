import cv2
import face_recognition
import numpy as np
import os
from database.connection import db

PROFILE_PIC_FOLDER = "dataset/"  # Ensure profile pictures are inside 'dataset/'

async def load_known_faces():
    """
    Loads known face encodings from stored profile pictures.
    Returns:
        - known_face_encodings (list): Encoded face vectors.
        - known_face_ids (list): Corresponding user IDs.
    """
    known_face_encodings = []
    known_face_ids = []

    try:
        profiles = await db["profile"].find({}, {"user_id": 1, "personal_details.profile_picture": 1}).to_list(None)
        print(f"🔄 Found {len(profiles)} profiles in the database.")

        for profile in profiles:
            user_id = profile.get("user_id", "Unknown")
            profile_pic_path = profile.get("personal_details", {}).get("profile_picture", None)

            if not profile_pic_path:
                print(f"⚠️ Skipping user {user_id} (No profile picture)")
                continue

            # ✅ Ensure full path is used
            full_path = os.path.normpath(profile_pic_path)  # Normalize path

            if not os.path.exists(full_path):
                print(f"❌ Profile picture not found for user {user_id}: {full_path}")
                continue

            print(f"📂 Loading face for user: {user_id} from {full_path}")

            img = cv2.imread(full_path)
            if img is None:
                print(f"⚠️ Could not read image for user {user_id}: {full_path}")
                continue

            face_locations = face_recognition.face_locations(img)
            if not face_locations:
                print(f"⚠️ No face detected in image: {full_path}")
                continue

            face_encodings = face_recognition.face_encodings(img, face_locations)
            if face_encodings:
                known_face_encodings.append(face_encodings[0])
                known_face_ids.append(user_id)
                print(f"✅ Face successfully loaded for user {user_id}")

        print(f"✅ Total loaded faces: {len(known_face_encodings)}")
        return known_face_encodings, known_face_ids

    except Exception as e:
        print(f"🔥 ERROR in load_known_faces(): {str(e)}")
        return [], []

def recognize_face(image, known_face_encodings, known_face_ids):
    """
    Recognizes a face in the given image.

    :param image: The captured image.
    :param known_face_encodings: List of known face encodings.
    :param known_face_ids: List of corresponding user IDs.
    :return: Tuple (Processed Image, User ID) or ('Unknown' if no match).
    """
    try:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)  # 🔥 Reduce tolerance
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances) if face_distances.size > 0 else -1

            if best_match_index != -1 and matches[best_match_index]:
                user_id = known_face_ids[best_match_index]
                return image, user_id

        return image, "Unknown"

    except Exception as e:
        print(f"🔥 ERROR in recognize_face(): {str(e)}")
        return image, "Unknown"
