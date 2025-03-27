from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional  # ✅ Correct imports

class LeaveBase(BaseModel):
    user_id: str  # Employee ID
    employee_name: str
    date: datetime  # Leave date
    leave_type: str  # "Sick Leave", "Casual Leave", "Annual Leave"
    reason: str
    status: Optional[str] = "Pending"  # Default status (Pending, Approved, Rejected)
    applied_at: datetime = datetime.now()  # Auto-filled when leave is applied
    approved_by: Optional[str] = None  # HR user_id (null if pending)

class LeaveReview(BaseModel):
    status: Literal["Approved", "Rejected"]
    hr_id: str
