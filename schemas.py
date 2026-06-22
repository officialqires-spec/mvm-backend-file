from pydantic import BaseModel

# Naya user banane ke liye (Ye pehle se tha)
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str

# NAYA: Login check karne ke liye (Sirf email aur password)
class UserLogin(BaseModel):
    email: str
    password: str