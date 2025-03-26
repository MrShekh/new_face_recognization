from pydantic import  EmailStr, Field
from datetime import date
from pydantic import BaseModel

class User(BaseModel):
    name: str
    company_email: EmailStr  # ✅ Ensure this field exists as 'company_email'
    password: str
    confirm_password: str  # This will not be stored in the database
    gender: str = Field(..., pattern="^(Male|Female|Other)$")
    role: str = Field(..., pattern="^(HR|Employee)$")
    department: str
    employee_id: str
    dob: date  # ✅ Correct date format

class LoginRequest(BaseModel):
    company_email: EmailStr  # ✅ Ensure the login model uses 'company_email'
    password: str
