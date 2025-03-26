from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date


class PersonalDetails(BaseModel):
    name: str
    caste: str
    state: str
    nationality: str
    blood_group: Optional[str] = None  # Optional field
    physical_disability: Optional[str] = None
    religion: str
    aadhaar_card: str
    profile_picture: str  # URL or Base64 Image

class ContactDetails(BaseModel):
    mobile_numbers: List[str]
    whatsapp_number: str
    personal_email: EmailStr
    address: str
    permanent_address: str
    state: Optional[str] = None
    country: Optional[str] = None
    district: Optional[str] = None
    pincode: str


class Education(BaseModel):
    tenth_school_name: str
    tenth_state: str
    tenth_total_marks: int
    tenth_certificate: str  # URL or Base64 Image
    tenth_board: str
    tenth_passing_month_year: str

    twelfth_school_name: str
    twelfth_state: str
    twelfth_total_marks: int
    twelfth_certificate: str
    twelfth_board: str
    twelfth_passing_month_year: str

    college_degree_certificate: str
    college_state: str
    college_district: str
    college_cgpa: float
    college_name: str

class Documents(BaseModel):
    aadhaar_card_photo: str
    pan_card_photo: str
    resume_cv: str
    passport_size_photo: str

class BankDetails(BaseModel):
    account_number: str
    account_holder_name: str
    state: str
    bank_name: str
    branch_name: str
    ifsc_code: str
    account_type: str
    passbook_photo: str

class Profile(BaseModel):
    user_id: str  # Link profile to a user
    personal_details: PersonalDetails
    contact_details: ContactDetails
    education: Education
    documents: Documents
    bank_details: BankDetails
