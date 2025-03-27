from fastapi import APIRouter, UploadFile, File, HTTPException
import cv2
import numpy as np
from datetime import datetime
import os
import traceback

from database.connection import db
from models.attendance import AttendanceBase
from facerecognition_module.detector import recognize_face, load_known_faces

router = APIRouter()

UPLOAD_DIR = "uploads/attendance/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

CHECK_IN_START = 9
CHECK_IN_END = 9.5  # 9:30 AM
CHECK_OUT_START = 17  # 5:00 PM

@router.post("/mark-attendance")
async def mark_attendance(file: UploadFile = File(...)):
    try:
        print("📸 Processing new attendance request...")

        image_bytes = await file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format!")

        known_face_encodings, known_face_ids = await load_known_faces()

        frame, user_id = recognize_face(img, known_face_encodings, known_face_ids)

        if user_id == "Unknown":
            raise HTTPException(status_code=400, detail="Face not recognized!")

        print(f"✅ Recognized User ID: {user_id}")

        return {"status": "success", "message": "Attendance Marked!", "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







### ✅ MARK CHECK-OUT ###
# @router.post("/mark-checkout/{user_id}")
# async def mark_checkout(user_id: str):
#     try:
#         now = datetime.now()
#         current_time = now.hour + now.minute / 60  # Convert time to float

#         if current_time < CHECK_OUT_TIME:
#             raise HTTPException(status_code=400, detail="Check-out is only allowed after 5:00 PM!")

#         # Find latest check-in record
#         attendance_record = db.attendance.find_one({"user_id": user_id, "check_out": None})
#         if not attendance_record:
#             raise HTTPException(status_code=400, detail="No check-in record found!")

#         check_in_time = attendance_record["check_in"]
#         total_hours = round((now - check_in_time).total_seconds() / 3600, 2)

#         # Update Attendance Record
#         db.attendance.update_one(
#             {"_id": attendance_record["_id"]},
#             {"$set": {"check_out": now, "total_working_hours": total_hours}}
#         )

#         return {"status": "success", "message": "Check-out successful!", "total_working_hours": total_hours}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


### ✅ ATTENDANCE REPORTS (DAILY, WEEKLY, MONTHLY, YEARLY) ###
@router.get("/attendance-report/{user_id}/{period}")
async def attendance_report(user_id: str, period: str):
    try:
        now = datetime.now()
        start_date = None

        if period == "daily":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            start_date = now - timedelta(days=now.weekday())  # Start of the week
        elif period == "monthly":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "yearly":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            raise HTTPException(status_code=400, detail="Invalid report period! Use daily, weekly, monthly, or yearly.")

        records = list(db.attendance.find({"user_id": user_id, "check_in": {"$gte": start_date}}))
        
        # Convert ObjectId & datetime to string for response
        for record in records:
            record["_id"] = str(record["_id"])
            record["check_in"] = record["check_in"].isoformat()
            if record["check_out"]:
                record["check_out"] = record["check_out"].isoformat()

        return {"status": "success", "records": records}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
