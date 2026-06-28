from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
# 🛑 ATOMIC FIX: Import password hashing library
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Create Database Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MVM School ERP Backend")

# ==========================================
# ⏱️ CRON JOB: AUTO-ABSENT SCHEDULER
# ==========================================
def auto_absent_job():
    db = SessionLocal()
    try:
        today_date = date.today().isoformat() # Format: YYYY-MM-DD
        
        # 1. Sirf 'Active' staff ka data nikalo
        active_staff = db.query(models.Staff).filter(models.Staff.status == "Active").all()
        
        for staff in active_staff:
            # 2. Check karo ki aaj ki attendance record exist karti hai ya nahi
            # ⚠️ Note: Ek baar confirm kar lena ki tumhare models.py me table ka naam 'Attendance' hi hai
            existing_record = db.query(models.Attendance).filter(
                models.Attendance.staff_id == staff.id,
                models.Attendance.date == today_date
            ).first()
            
            # 3. Agar attendance nahi mili, toh Auto-Absent (A) mark kar do
            if not existing_record:
                absent_record = models.Attendance(
                    staff_id=staff.id,
                    name=staff.name,
                    date=today_date,
                    time="Auto",
                    status="A"
                )
                db.add(absent_record)
        
        db.commit()
        print(f"✅ Auto-absent job executed successfully for {today_date}")
    except Exception as e:
        print(f"❌ Cron Job Error: {e}")
    finally:
        db.close()

@app.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()
    # Roz dopahar 12:00 PM baje trigger hoga
    scheduler.add_job(auto_absent_job, 'cron', hour=12, minute=0)
    scheduler.start()

# --- CORS SECURITY (Frontend ko connect hone ki permission) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Production me isko apne github/vercel url se replace kar dena
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "MVM School ERP API is LIVE! 🚀"}

# ==========================================
# 🏫 STUDENT APIs (Connected to Admin Dashboard)
# ==========================================
@app.get("/api/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    # Formatting for frontend compatibility
    return [{
        "id": s.id, "name": s.name, "class": s.class_name, "section": s.section,
        "phone": s.phone, "father": s.father, "email": s.email, "password": s.password, "status": s.status
    } for s in students]

@app.post("/api/students")
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id == student.id).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    # 🛑 ATOMIC FIX: Hash the password before saving to DB
    hashed_password = get_password_hash(student.password)
    
    new_student = models.Student(
        id=student.id, name=student.name, class_name=student.class_name,
        section=student.section, phone=student.phone, father=student.father,
        email=student.email, password=hashed_password, status=student.status
    )
    db.add(new_student)
    db.commit()
    return {"message": "Student Added Successfully", "id": new_student.id}

@app.put("/api/students/{student_id}")
def update_student(student_id: str, student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    db_student.name = student.name
    db_student.class_name = student.class_name
    db_student.section = student.section
    db_student.phone = student.phone
    db_student.father = student.father
    db_student.email = student.email
    
    # 🛑 Only hash and update if a new password is provided
    if student.password and not student.password.startswith("$2b$"): 
        db_student.password = get_password_hash(student.password)
    else:
        db_student.password = student.password

    # 🛑 ATOMIC FIX: Sync updated name to all relational ledgers
    db.query(models.FeeLedger).filter(models.FeeLedger.student_id == student_id).update({"student_name": student.name})
    db.query(models.HomeworkSubmission).filter(models.HomeworkSubmission.student_id == student_id).update({"student_name": student.name})
    db.query(models.DisciplineLog).filter(models.DisciplineLog.student_id == student_id).update({"student_name": student.name})
    
    db.commit()
    return {"message": "Student & Related Ledgers Updated"}

# ==========================================
# 👨‍💼 STAFF APIs (Connected to HR Dashboard)
# ==========================================
@app.get("/api/staff")
def get_staff(db: Session = Depends(get_db)):
    return db.query(models.Staff).all()

@app.post("/api/staff")
def create_staff(staff: schemas.StaffCreate, db: Session = Depends(get_db)):
    new_staff = models.Staff(**staff.dict())
    db.add(new_staff)
    db.commit()
    return {"message": "Staff Hired"}

# ==========================================
# 📢 NOTICES & BROADCASTS
# ==========================================
@app.get("/api/notices")
def get_notices(db: Session = Depends(get_db)):
    return db.query(models.NoticeBoard).all()

@app.post("/api/notices")
def create_notice(notice: schemas.NoticeCreate, db: Session = Depends(get_db)):
    new_notice = models.NoticeBoard(**notice.dict())
    db.add(new_notice)
    db.commit()
    return {"message": "Broadcast Sent"}
