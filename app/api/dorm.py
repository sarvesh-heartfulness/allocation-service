from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uuid

from schema import DormPydanticRead, DormPydanticWrite, DormPydanticUpdate
from models import Dorm
from config.db import get_db

router = APIRouter(tags=["dorms"])

# Should add a helper method that returns all necessary information
@router.get("/", response_model=List[DormPydanticRead], status_code=status.HTTP_200_OK)
def list_dorms(
    db: Session = Depends(get_db),
    limit: int = 20,
    skip: int = 0,
    active: Optional[bool] = Query(None),):
    '''
    List all the dorms
    '''

    # apply filters if any
    dorms = db.query(Dorm).order_by(desc(Dorm.created_at))
    if active is not None:
        dorms = dorms.filter(Dorm.active == active)

    # apply pagination
    dorms = dorms.offset(skip).limit(limit).all()
    return dorms

@router.get("/{dorm_id}/", response_model=DormPydanticRead, status_code=status.HTTP_200_OK)
def read_dorm(
    dorm_id: uuid.UUID,
    db: Session = Depends(get_db)):
    '''
    Get a dorm by id
    '''
    dorm = db.query(Dorm).filter(Dorm.id==dorm_id).one_or_none()
    if dorm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Dorm not found')
    return dorm

@router.post("/", response_model=DormPydanticRead, status_code=status.HTTP_201_CREATED)
def create_dorm(
    dorm: DormPydanticWrite,
    db: Session = Depends(get_db)):
    '''
    Create a new dorm
    '''
    try:
        db_item = Dorm(**dorm.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str('Dorm already exists'))
    return db_item

# Partial update not possible YET
@router.patch("/{dorm_id}/", response_model=DormPydanticRead, status_code=status.HTTP_200_OK)
def update_dorm(
    dorm_id: uuid.UUID,
    dorm: DormPydanticUpdate,
    db: Session = Depends(get_db)):
    '''
    Update a dorm
    '''
    existing_dorm = db.query(Dorm).filter(Dorm.id==dorm_id).one_or_none()
    if existing_dorm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Dorm not found')
    
    for var, value in vars(dorm).items():
        setattr(existing_dorm, var, value) if value else None
    
    try:
        db.commit()
        db.refresh(existing_dorm)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    return existing_dorm