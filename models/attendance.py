from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class AttendanceBase(BaseModel):
    user_id: str  # ✅ Replaced `emp_id` with `user_id`
    employee_name: str
    check_in: Optional[datetime] = None
    status: Optional[str] = None  # "On-Time", "Late"
    check_out: Optional[datetime] = None
    total_working_hours: Optional[float] = None