import cv2
import requests
import threading
import time

URL = "http://127.0.0.1:8000/api/mark-attendance"

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Error: Could not open camera.")
    exit()

is_sending = False  # Prevent multiple API calls at once

def send_attendance(frame):
    """Send face image to API in a separate thread."""
    global is_sending
    is_sending = True  # Mark as sending
    
    _, img_encoded = cv2.imencode('.jpg', frame)
    
    try:
        start_time = time.time()
        response = requests.post(URL, files={"file": ("image.jpg", img_encoded.tobytes(), "image/jpeg")})
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ Attendance Marked: {response.json()}")
        else:
            print(f"❌ Attendance Failed: {response.text}")

        print(f"⏳ API Response Time: {round(end_time - start_time, 2)} seconds")

    except Exception as e:
        print(f"❌ Error sending attendance: {str(e)}")
    
    is_sending = False  # Ready for next request

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Error: Could not capture frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Camera Preview", frame)

    # Send request **ONLY** if no other request is in progress
    if len(faces) > 0 and not is_sending:
        print("📸 Face detected, sending image for recognition...")
        threading.Thread(target=send_attendance, args=(frame,)).start()

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
