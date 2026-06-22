import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ye line .env file se password nikalegi
load_dotenv() 

# 🚨 BULLETPROOF URL (Password chhupa hua hai) 🚨
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# sslmode ko engine ke andar direct pass kar rahe hain
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()