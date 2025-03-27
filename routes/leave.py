from fastapi import APIRouter, HTTPException, Depends, Path, Body  # ✅ Added Body import
from datetime import datetime
from database.connection import db
from models.leave import LeaveBase, LeaveReview  # ✅ Import models correctly
from models.user import User  # ✅ Assuming you have user roles stored
from bson import ObjectId
from typing import List

router = APIRouter()

### **🔹 Employee Applies for Leave**
@router.post("/apply-leave")
async def apply_leave(leave_data: LeaveBase):
    """Employee applies for leave request"""
    existing_user = db.users.find_one({"user_id": leave_data.user_id})

    if not existing_user:
        raise HTTPException(status_code=400, detail="User not found!")

    leave_entry = leave_data.dict()
    leave_entry["_id"] = str(ObjectId())  # Generate MongoDB Object ID
    leave_entry["status"] = "Pending"  # Default status

    db.leave.insert_one(leave_entry)

    return {"status": "success", "message": "Leave applied successfully!"}

### **🔹 HR Views All Pending Leaves**
@router.get("/pending-leaves")
async def get_pending_leaves():
    """HR retrieves all pending leave requests"""
    leaves = list(db.leave.find({"status": "Pending"}))  # ✅ Convert to list properly
    for leave in leaves:
        leave["_id"] = str(leave["_id"])  # Convert ObjectId to string

    return {"status": "success", "pending_leaves": leaves}

### **🔹 HR Approves or Rejects Leave (✅ FIXED)**
@router.put("/review-leave/{leave_id}")
async def review_leave(
    leave_id: str = Path(..., description="MongoDB Leave Document ID"),
    review: LeaveReview = Body(...)
):
    try:
        # Check if leave exists
        leave = db.leave.find_one({"_id": ObjectId(leave_id)})
        if not leave:
            raise HTTPException(status_code=404, detail="Leave request not found.")

        # ✅ FIX: Remove `await` from `update_one()`
        result = db.leave.update_one(
            {"_id": ObjectId(leave_id)},
            {"$set": {"status": review.status, "approved_by": review.hr_id, "reviewed_at": datetime.utcnow()}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Leave update failed.")

        return {"status": "success", "message": f"Leave {review.status} by HR {review.hr_id}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### **🔹 Employee Views Their Leave Requests**
@router.get("/my-leaves/{user_id}")
async def get_my_leaves(user_id: str):
    """Employee can check their own leave history"""
    leaves = list(db.leave.find({"user_id": user_id}))  # ✅ Convert to list properly
    for leave in leaves:
        leave["_id"] = str(leave["_id"])  # Convert ObjectId to string

    return {"status": "success", "leaves": leaves}
