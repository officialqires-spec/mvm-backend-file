from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal

# Database generate karne ka code
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="School ERP Backend")

# --- NAYA: CORS SECURITY (Gate Pass) ---
# Ye frontend ko backend se data lene aur dene ki permission deta hai
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Abhi ke liye hum kisi bhi frontend ko allow kar rahe hain
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
    return {"message": "Welcome to Adarsh's School ERP API!"}

# Naya User banane ka Rasta (Bug Fixed)
@app.post("/create-user/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Bug Fix: Pehle check karo ki email database me hai ya nahi
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Ye email pehle se registered hai!")
        
    new_user = models.User(name=user.name, email=user.email, password=user.password, role=user.role)
    db.add(new_user)       
    db.commit()            
    db.refresh(new_user)   
    return {"message": "User ekdum successfully ban gaya!", "user_name": new_user.name, "role": new_user.role}

# --- NAYA: LOGIN CHECK KARNE KA RASTA ---
@app.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # Database me jao aur dekho kya is email aur password wala koi user hai?
    db_user = db.query(models.User).filter(
        models.User.email == user.email, 
        models.User.password == user.password
    ).first()
    
    # Agar user mil gaya
    if db_user:
        return {"message": "Login Successful!", "user_name": db_user.name, "role": db_user.role}
    # Agar galat password dala
    else:
        raise HTTPException(status_code=401, detail="Galat Email ya Password dala hai bhai!")