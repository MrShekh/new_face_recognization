from fastapi import APIRouter, HTTPException, Response, Depends
from database.connection import users_collection
from models.user import User, LoginRequest
from core.security import (
    hash_password,
    verify_password,
    create_jwt_token,
    set_jwt_cookie,
)
from bson import ObjectId

auth_router = APIRouter()

# ✅ Register API
@auth_router.post("/register")
async def register(user: User):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    existing_user = users_collection.find_one({"company_email": user.company_email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Company email already registered")

    hashed_pwd = hash_password(user.password)

    new_user = {
        "name": user.name,
        "company_email": user.company_email,
        "password": hashed_pwd,
        "gender": user.gender,
        "role": user.role,
        "department": user.department,
        "employee_id": user.employee_id,
        "dob": str(user.dob),  # Convert date to string for MongoDB
    }

    users_collection.insert_one(new_user)
    return {"message": "User registered successfully"}

# ✅ Login API (Saves Token in Cookies)
@auth_router.post("/login")
async def login(user: LoginRequest, response: Response):
    user_data = users_collection.find_one({"company_email": user.company_email})
    if not user_data or not verify_password(user.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ✅ Generate JWT Token
    token = create_jwt_token({"user_id": str(user_data["_id"]), "role": user_data["role"]})

    # ✅ Store token in HTTP-only Cookie
    set_jwt_cookie(response, token)

    return {"message": "Login successful"}
