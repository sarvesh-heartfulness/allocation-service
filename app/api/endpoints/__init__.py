from fastapi import APIRouter
from dotenv import load_dotenv
import os
from config.db import check_db_connection

router = APIRouter()
load_dotenv()

@router.get("/")
def root():
    return {"message": "Allocation Service APIs are up and running!",
            "env": os.getenv("ENV")}

@router.get("/checkdb")
def checkdb():
    return {"message": "Database is connected!"} if check_db_connection() else {"message": "Database is not connected!"}