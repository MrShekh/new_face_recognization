from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class AttendanceBase(BaseModel):
    emp_id: str  # ✅ Using `emp_id` instead of `user_id`
    employee_name: str
    check_in: Optional[datetime] = None
    status: Optional[str] = None  # "On-Time", "Late"
    check_out: Optional[datetime] = None
    total_working_hours: Optional[float] = None


