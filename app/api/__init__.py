from fastapi import APIRouter
from dotenv import load_dotenv
import os
from config.db import check_db_connection
from api.dorm import router as dorm_router

router = APIRouter()
load_dotenv()

@router.get("/")
def check():
    return {"message": "Allocation Service APIs are up and running!"}

@router.get("/checkdb")
def check_database_connection():
    return {"message": "Database is connected!"} if check_db_connection() else {"message": "Database is not connected!"}