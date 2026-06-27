from sqlalchemy import Column, Integer, String, Boolean, Float, Text, Date, Time, ForeignKey, DateTime
from database import Base
import datetime

# ==========================================
# 🏫 1. CORE USER MODELS (Admin, HR, Student)
# ==========================================

class Student(Base):
    __tablename__ = "students"
    # Matches 'system_class_roster' & 'adminStudentsDB'
    id = Column(String, primary_key=True, index=True) # E.g., STU-2026-1234
    name = Column(String, index=True)
    class_name = Column(String) # E.g., Class 10
    section = Column(String) # E.g., A
    phone = Column(String)
    father = Column(String)
    email = Column(String, nullable=True)
    password = Column(String)
    status = Column(String, default="Active")

class Staff(Base):
    __tablename__ = "staff"
    # Matches 'hrStaffDB'
    id = Column(String, primary_key=True, index=True) # E.g., T-101, HR-001
    name = Column(String, index=True)
    dept = Column(String) # Teacher, HR, Transport, Admin
    role = Column(String) # PGT Science, Manager, etc.
    phone = Column(String)
    salary = Column(Integer)
    email = Column(String, unique=True, nullable=True)
    password = Column(String)
    status = Column(String, default="Active")

# ==========================================
# 💰 2. FINANCE & FEES MODELS (Owner, Admin)
# ==========================================

class FeeLedger(Base):
    __tablename__ = "fee_ledger"
    id = Column(Integer, primary_key=True, index=True)
    # 🛑 ATOMIC FIX: Foreign Key with Cascade Delete (Zombie Data Prevention)
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), index=True)
    student_name = Column(String)
    total_payable = Column(Integer, default=0)
    paid = Column(Integer, default=0)
    status = Column(String, default="Pending")

class FeeTransaction(Base):
    __tablename__ = "fee_transactions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), index=True)
    # 🛑 ATOMIC FIX: Proper DateTime for financial analytics
    date = Column(DateTime, default=datetime.datetime.utcnow)
    amount = Column(Integer)
    mode = Column(String) 
    receipt_no = Column(String)

class PettyCash(Base):
    __tablename__ = "petty_cash"
    # Matches 'adminPettyCashDB'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    amount = Column(Integer)
    given_to = Column(String)
    time = Column(String)

# ==========================================
# 📅 3. ATTENDANCE & LEAVES (HR, Teacher)
# ==========================================

class StaffAttendance(Base):
    __tablename__ = "staff_attendance"
    # Matches 'staff_attendance_db'
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(String, index=True)
    name = Column(String)
    date = Column(String)
    time = Column(String)
    status = Column(String) # P, A, halfday

class StudentAttendance(Base):
    __tablename__ = "student_attendance"
    id = Column(Integer, primary_key=True, index=True)
    # 🛑 ATOMIC FIX: Foreign Key added
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), index=True)
    date = Column(String)
    status = Column(String) 
    marked_by = Column(String)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    # Merges both 'staffLeaveDB' and 'leaveRequests' (Students)
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(String, index=True) # Staff ID or Student ID
    requester_name = Column(String)
    requester_type = Column(String) # "Staff" or "Student"
    start_date = Column(String)
    end_date = Column(String)
    reason = Column(Text)
    status = Column(String, default="Pending") # Pending, Approved, Rejected

# ==========================================
# 🎓 4. ACADEMICS & TEACHER TOOLS (Teacher, VP)
# ==========================================

class TeacherMapping(Base):
    __tablename__ = "teacher_mappings"
    # Matches 'teacher_class_mapping'
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, index=True)
    teacher_name = Column(String)
    class_name = Column(String) # E.g., Class 10-A
    subject = Column(String)

class Homework(Base):
    __tablename__ = "homeworks"
    # Matches 'assignedTeacherHW'
    id = Column(String, primary_key=True, index=True) # HW-1234
    teacher_id = Column(String)
    class_name = Column(String)
    subject = Column(String)
    title = Column(String)
    description = Column(Text)
    due_date = Column(String)
    type = Column(String) # Assignment, Project

class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"
    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(String, index=True)
    # 🛑 ATOMIC FIX: Foreign Key added
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), index=True)
    student_name = Column(String)
    attachment_link = Column(String)
    submission_date = Column(String)

class StudentMarks(Base):
    __tablename__ = "student_marks"
    id = Column(Integer, primary_key=True, index=True)
    # 🛑 ATOMIC FIX: Foreign Key added
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), index=True)
    term = Column(String) 
    subject = Column(String)
    theory = Column(Integer, default=0)
    internal = Column(Integer, default=0)
    total = Column(Integer, default=0)

# ==========================================
# ⚖️ 5. DISCIPLINE, AUDITS & NOTICES (Principal, VP)
# ==========================================

class NoticeBoard(Base):
    __tablename__ = "notices"
    # Matches 'globalNoticesDB'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    text = Column(Text)
    sender = Column(String) # HR Dept, Principal, Admin
    date = Column(String)
    time = Column(String)

class DisciplineLog(Base):
    __tablename__ = "discipline_logs"
    id = Column(Integer, primary_key=True, index=True)
    # 🛑 ATOMIC FIX: Foreign Key added
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), index=True)
    student_name = Column(String)
    action = Column(String) 
    reason = Column(Text)
    reported_by = Column(String)
    severity = Column(String)

class Grievance(Base):
    __tablename__ = "grievances"
    # Matches 'grievanceLog'
    id = Column(String, primary_key=True, index=True) # GRV-1234
    sender = Column(String)
    type = Column(String) # Bullying, Infrastructure
    target = Column(String) # Principal, VP, HR
    text = Column(Text)
    status = Column(String, default="Pending")

class TeacherAudit(Base):
    __tablename__ = "teacher_audits"
    # Matches 'teacherAuditDB'
    id = Column(Integer, primary_key=True, index=True)
    teacher_name = Column(String)
    rating = Column(String) # Excellent, Needs Improvement
    color = Column(String)
    time = Column(String)

# ==========================================
# 🚌 6. TRANSPORT & FRONT DESK (Admin, Transport)
# ==========================================

class BusFleet(Base):
    __tablename__ = "bus_fleet"
    # Matches 'transport_fleet_db'
    id = Column(Integer, primary_key=True, index=True)
    bus_no = Column(String)
    driver = Column(String)
    route = Column(String)
    capacity = Column(Integer)
    status = Column(String, default="Active")

class Visitor(Base):
    __tablename__ = "visitors"
    # Matches 'adminVisitorDB'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    purpose = Column(String)
    time = Column(String)

class HelpdeskTicket(Base):
    __tablename__ = "helpdesk_tickets"
    # Matches 'helpdesk_tickets_db'
    id = Column(String, primary_key=True, index=True)
    issue = Column(Text)
    sender = Column(String)
    time = Column(String)
    status = Column(String, default="Pending")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    # Matches 'schoolChatDB_Teacher_Student'
    id = Column(Integer, primary_key=True, index=True)
    chat_room_id = Column(String, index=True) # e.g., "S.K. Mishra_STU-123"
    sender = Column(String) # "Teacher" or "Student"
    text = Column(Text)
    time = Column(String)

# 🚀 END OF MEGA MODELS 🚀
