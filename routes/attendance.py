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

# Directory for storing attendance images
UPLOAD_DIR = "uploads/attendance/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Office Hours
CHECK_IN_START = 9
CHECK_IN_END = 9.5  # 9:30 AM
CHECK_OUT_START = 17  # 5:00 PM

@router.post("/mark-attendance")
async def mark_attendance(file: UploadFile = File(...)):
    try:
        print("📸 Processing new attendance request...")

        # ✅ Read Image
        image_bytes = await file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print("❌ ERROR: Invalid image format!")
            raise HTTPException(status_code=400, detail="Invalid image format!")

        # ✅ Load Known Faces from Database
        known_face_encodings, known_face_ids = await load_known_faces()
        print(f"🔄 Loaded {len(known_face_encodings)} known faces from database.")

        # ✅ Perform Face Recognition
        frame, emp_id = recognize_face(img, known_face_encodings, known_face_ids)

        if emp_id == "Unknown":
            print("❌ ERROR: Face not recognized!")
            raise HTTPException(status_code=400, detail="Face not recognized. Please try again!")

        print(f"✅ Recognized Employee ID: {emp_id}")

        # ✅ Check Database Connection
        if db is None:
            print("❌ ERROR: Database connection is None!")
            raise HTTPException(status_code=500, detail="Database connection is not initialized!")

        # ✅ Fetch Employee Details from 'users' Collection
        print(f"🔍 Searching for Employee ID: {emp_id} in 'users' collection")
        user = await db["users"].find_one({"emp_id": emp_id}, {"name": 1})

        if not user:
            print(f"❌ ERROR: No user found with Employee ID: {emp_id}")
            raise HTTPException(status_code=400, detail="Employee not found in the database!")

        employee_name = user.get("name", "Unknown")

        # ✅ Get Current Time
        current_time = datetime.now()
        current_hour = current_time.hour + (current_time.minute / 60)

        # ✅ Check If Employee Already Checked-In
        existing_record = await db["attendance"].find_one({"emp_id": emp_id, "check_out": None})

        if existing_record:
            # ✅ Check-Out Logic (Allowed Only After 5:00 PM)
            if current_hour < CHECK_OUT_START:
                print("❌ ERROR: Check-Out is allowed only after 5:00 PM!")
                raise HTTPException(status_code=400, detail="Check-Out is allowed only after 5:00 PM!")

            check_in_time = existing_record["check_in"]
            total_hours = (current_time - check_in_time).total_seconds() / 3600

            # ✅ Update Attendance Record (Check-Out)
            await db["attendance"].update_one(
                {"_id": existing_record["_id"]},
                {"$set": {"check_out": current_time, "total_working_hours": round(total_hours, 2)}}
            )

            return {
                "status": "success",
                "message": "✅ Check-Out Successful!",
                "emp_id": emp_id,
                "employee_name": employee_name,
                "total_working_hours": round(total_hours, 2)
            }

        # ✅ Determine Check-In Status
        if current_hour < CHECK_IN_START:
            status = "Early"
        elif CHECK_IN_START <= current_hour <= CHECK_IN_END:
            status = "On-Time"
        else:
            status = "Late"

        # ✅ Save Attendance Record (Check-In)
        attendance_record = AttendanceBase(
            emp_id=emp_id,
            employee_name=employee_name,
            check_in=current_time,
            status=status,
            check_out=None,
            total_working_hours=None
        )

        await db["attendance"].insert_one(attendance_record.dict())

        return {
            "status": "success",
            "message": "✅ Check-In Successful!",
            "emp_id": emp_id,
            "employee_name": employee_name,
            "status": status
        }

    except Exception as e:
        print("🔥 ERROR:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
