from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)  # ✅ Async Client
db = client["attendance_system"]

# Collections
users_collection = db["users"]
profiles_collection = db["profiles"]
attendance_collection = db["attendance"]  # If needed
