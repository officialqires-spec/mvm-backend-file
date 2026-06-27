from pydantic import BaseModel, Field
from typing import Optional, List

# ==========================================
# 1. CORE MODELS (Students & Staff)
# ==========================================
class StudentCreate(BaseModel):
    id: str
    name: str
    class_name: str = Field(alias="class") # Frontend bhejega 'class', backend padhega 'class_name'
    section: str
    phone: str
    father: str
    email: Optional[str] = None
    password: str
    status: Optional[str] = "Active"

class StudentResponse(StudentCreate):
    class Config:
        from_attributes = True
        populate_by_name = True

class StaffCreate(BaseModel):
    id: str
    name: str
    dept: str
    role: str
    phone: str
    salary: int
    email: Optional[str] = None
    password: str
    status: Optional[str] = "Active"

class StaffResponse(StaffCreate):
    class Config:
        from_attributes = True

# ==========================================
# 2. FINANCE MODELS (Fees & Petty Cash)
# ==========================================
class FeeLedgerCreate(BaseModel):
    student_id: str
    student_name: str
    total_payable: int
    paid: Optional[int] = 0
    status: Optional[str] = "Pending"

class FeeTransactionCreate(BaseModel):
    student_id: str
    amount: int
    mode: str
    receipt_no: str

class PettyCashCreate(BaseModel):
    description: str
    amount: int
    given_to: str
    time: str

# ==========================================
# 3. LEAVES & NOTICES 
# ==========================================
class LeaveRequestCreate(BaseModel):
    requester_id: str
    requester_name: str
    requester_type: str
    start_date: str
    end_date: str
    reason: str
    status: Optional[str] = "Pending"

class NoticeCreate(BaseModel):
    title: str
    text: str
    sender: str
    date: str
    time: str
