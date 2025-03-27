from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from bson import ObjectId
from database.connection import db
import requests
import shutil
import os

profile_router = APIRouter()

# ✅ Define Directories
UPLOAD_DIR = "uploads/"
DATASET_DIR = "dataset"  # ✅ Profile Pictures should go here
DOCUMENTS_DIR = os.path.join(UPLOAD_DIR, "documents")
CERTIFICATES_DIR = os.path.join(UPLOAD_DIR, "certificates")

# ✅ Ensure directories exist
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(CERTIFICATES_DIR, exist_ok=True)

def get_location_from_pincode(pincode: str):
    """Fetch district, state, and country from pincode"""
    url = f"https://api.postalpincode.in/pincode/{pincode}"
    response = requests.get(url).json()
    
    if response and response[0]['Status'] == 'Success':
        return {
            "district": response[0]['PostOffice'][0]['District'],
            "state": response[0]['PostOffice'][0]['State'],
            "country": response[0]['PostOffice'][0]['Country']
        }
    return None

def save_file(upload: UploadFile, folder: str):
    """Save uploaded file and return its relative path"""
    file_location = os.path.join(folder, upload.filename)  # ✅ Correct Path
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    
    return file_location.replace("\\", "/")  # ✅ Convert Windows paths to UNIX format

# ✅ 🚀 Create Profile (POST)
@profile_router.post("/profile")
async def create_profile(
    user_id: str = Form(...),
    name: str = Form(...),
    caste: str = Form(...),
    state: str = Form(...),
    nationality: str = Form(...),
    blood_group: Optional[str] = Form(None),
    physical_disability: str = Form(...),
    religion: str = Form(...),
    aadhaar_card: str = Form(...),

    profile_picture: UploadFile = File(...),

    mobile_numbers: List[str] = Form(...),
    whatsapp_number: str = Form(...),
    personal_email: str = Form(...),
    address: str = Form(...),
    permanent_address: str = Form(...),
    pincode: str = Form(...),

    # 🔹 Education Details
    tenth_school_name: str = Form(...),
    tenth_state: str = Form(...),
    tenth_total_marks: int = Form(...),
    tenth_board: str = Form(...),
    tenth_passing_month_year: str = Form(...),

    twelfth_school_name: str = Form(...),
    twelfth_state: str = Form(...),
    twelfth_total_marks: int = Form(...),
    twelfth_board: str = Form(...),
    twelfth_passing_month_year: str = Form(...),

    college_state: str = Form(...),
    college_district: str = Form(...),
    college_cgpa: float = Form(...),
    college_name: str = Form(...),

    # 🔹 Bank Details
    account_number: str = Form(...),
    account_holder_name: str = Form(...),
    bank_state: str = Form(...),
    bank_name: str = Form(...),
    branch_name: str = Form(...),
    ifsc_code: str = Form(...),
    account_type: str = Form(...)
):
    """Handles profile creation and stores uploaded files"""

    # Get location data from pincode
    location_data = get_location_from_pincode(pincode)
    if not location_data:
        raise HTTPException(status_code=400, detail="Invalid Pincode")

    # Check if profile already exists
    existing_profile = db.profile.find_one({"user_id": user_id})
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")

    # ✅ Save profile picture in dataset folder
    profile_pic_path = save_file(profile_picture, DATASET_DIR)

    # Insert into MongoDB
    profile_data = {
        "user_id": user_id,
        "personal_details": {
            "name": name,
            "caste": caste,
            "state": state,
            "nationality": nationality,
            "blood_group": blood_group,
            "physical_disability": physical_disability,
            "religion": religion,
            "aadhaar_card": aadhaar_card,
            "profile_picture": profile_pic_path,  # ✅ Stored as dataset/image.jpg
        },
        "contact_details": {
            "mobile_numbers": mobile_numbers,
            "whatsapp_number": whatsapp_number,
            "personal_email": personal_email,
            "address": address,
            "permanent_address": permanent_address,
            "pincode": pincode,
            "state": location_data["state"],
            "district": location_data["district"],
            "country": location_data["country"]
        },
        "education": {
            "tenth": {
                "school_name": tenth_school_name,
                "state": tenth_state,
                "total_marks": tenth_total_marks,
                "board": tenth_board,
                "passing_month_year": tenth_passing_month_year
            },
            "twelfth": {
                "school_name": twelfth_school_name,
                "state": twelfth_state,
                "total_marks": twelfth_total_marks,
                "board": twelfth_board,
                "passing_month_year": twelfth_passing_month_year
            },
            "college": {
                "state": college_state,
                "district": college_district,
                "cgpa": college_cgpa,
                "name": college_name
            }
        },
        "bank_details": {
            "account_number": account_number,
            "account_holder_name": account_holder_name,
            "state": bank_state,
            "bank_name": bank_name,
            "branch_name": branch_name,
            "ifsc_code": ifsc_code,
            "account_type": account_type
        }
    }

    profile_id = db.profile.insert_one(profile_data).inserted_id
    return {"message": "Profile created successfully", "profile_id": str(profile_id)}

# ✅ 🚀 Get Profile (GET)
@profile_router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    profile = db.profile.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Convert ObjectId to string
    profile["_id"] = str(profile["_id"])
    
    # Normalize file path
    if "profile_picture" in profile["personal_details"]:
        profile["personal_details"]["profile_picture"] = profile["personal_details"]["profile_picture"].replace("\\", "/")
    
    return profile

# ✅ 🚀 Serve Profile Picture (GET)
from fastapi.responses import FileResponse

@profile_router.get("/profile-picture/{filename}")
async def get_profile_picture(filename: str):
    file_path = os.path.join(DATASET_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(file_path)

# ✅ 🚀 Update Profile Picture (PUT)
@profile_router.put("/profile/{user_id}")
async def update_profile_picture(user_id: str, profile_picture: UploadFile = File(...)):
    """Update profile picture in dataset folder"""

    # ✅ Save new profile picture in dataset folder
    profile_pic_path = save_file(profile_picture, DATASET_DIR)

    # ✅ Correct MongoDB update
    updated_profile = db.profile.find_one_and_update(
        {"user_id": user_id},
        {"$set": {"personal_details.profile_picture": profile_pic_path}},
        return_document=True
    )

    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"message": "Profile picture updated successfully", "profile_picture": profile_pic_path}
