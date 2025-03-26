import cv2
import face_recognition
import numpy as np
import os
from database.connection import db

# ✅ Define the folder where profile pictures are stored
PROFILE_PIC_FOLDER = "uploads/profile_pictures/"

async def load_known_faces():
    """
    Loads known face encodings from locally stored profile pictures.
    Returns:
        - known_face_encodings (list): Encoded face vectors.
        - known_face_ids (list): Corresponding employee IDs.
    """
    known_face_encodings = []
    known_face_ids = []

    try:
        # ✅ Fetch profiles with user_id and profile picture from MongoDB
        profiles = await db["profile"].find({}, {"user_id": 1, "personal_details.profile_picture": 1}).to_list(None)
        print(f"🔄 Found {len(profiles)} profiles in the database.")

        for profile in profiles:
            user_id = profile.get("user_id", "Unknown")
            profile_pic_path = profile.get("personal_details", {}).get("profile_picture", None)

            if not profile_pic_path:
                print(f"⚠️ Skipping user {user_id} (No profile picture)")
                continue

            # ✅ Ignore URLs (Only work with local images)
            if profile_pic_path.startswith("http"):
                print(f"❌ Skipping user {user_id} (Profile picture is a URL, expected local file)")
                continue

            # ✅ Fix duplicate folder paths issue
            if profile_pic_path.startswith(PROFILE_PIC_FOLDER):
                profile_pic_path = profile_pic_path.replace(PROFILE_PIC_FOLDER, "", 1)

            # ✅ Construct the correct full path
            full_path = os.path.join(PROFILE_PIC_FOLDER, profile_pic_path)

            if not os.path.exists(full_path):
                print(f"❌ Profile picture not found for user {user_id}: {full_path}")
                continue

            print(f"📂 Loading face for user: {user_id} from {full_path}")

            # ✅ Load the image
            img = cv2.imread(full_path)
            if img is None:
                print(f"⚠️ Could not read image for user {user_id}: {full_path}")
                continue

            # ✅ Detect faces in the image
            face_locations = face_recognition.face_locations(img)
            if not face_locations:
                print(f"⚠️ No face detected in image: {full_path}")
                continue

            # ✅ Encode the face
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
            # ✅ Compare with stored face encodings
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances) if face_distances.size > 0 else -1

            if best_match_index != -1 and matches[best_match_index]:
                user_id = known_face_ids[best_match_index]
                return image, user_id  # ✅ Return `user_id`

        return image, "Unknown"

    except Exception as e:
        print(f"🔥 ERROR in recognize_face(): {str(e)}")
        return image, "Unknown"
