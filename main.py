from fastapi import FastAPI
from routes.auth import auth_router
from routes.profile import profile_router
from routes.attendance import router as attendance_router
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(profile_router, prefix="/api", tags=["Profile"])  # ✅ Prefix applied
app.include_router(attendance_router, prefix="/api")

# ✅ Ensure `uploads/` directory exists
os.makedirs("uploads/profile_pictures", exist_ok=True)
os.makedirs("uploads/attendance", exist_ok=True)

# ✅ Serve static files from "uploads"
app.mount("/uploads", StaticFiles(directory="uploads", html=True), name="uploads")


@app.get("/")
def home():
    return {"message": "Welcome to AI Attendance System"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
