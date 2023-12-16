from fastapi import APIRouter, Depends, HTTPException, status, Query, Security
from fastapi.security import APIKeyHeader
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid

from schema import DormPydanticRead, DormPydanticWrite, DormPydanticUpdate, PaginatedDormResponse
from models import Dorm
from config.db import get_db
from deps import is_authenticated

router = APIRouter()
authorization_token = APIKeyHeader(name='Authorization', scheme_name='Authorization')
x_client_id = APIKeyHeader(name='X-Client-Id', scheme_name='X-Client-Id')

# Should add a helper method that returns all necessary information
@router.get("/", response_model=PaginatedDormResponse, status_code=status.HTTP_200_OK)
def list_dorms(
    db: Session = Depends(get_db),
    page_size: int = Query(20, gt=0, le=100),
    page: int = Query(1, gt=0),
    active: Optional[bool] = Query(None),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
    '''
    List all the dorms
    '''

    # apply filters if any
    dorms = db.query(Dorm).order_by(desc(Dorm.created_at))
    if active is not None:
        dorms = dorms.filter(Dorm.active == active)
    count = dorms.count()

    # apply pagination
    dorms = dorms.slice((page-1)*page_size, page*page_size).all()
    return {"count": count, "results": dorms}

@router.get("/{dorm_id}/", response_model=DormPydanticRead, status_code=status.HTTP_200_OK)
def read_dorm(
    dorm_id: uuid.UUID,
    db: Session = Depends(get_db),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
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
    db: Session = Depends(get_db),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
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
    db: Session = Depends(get_db),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
    '''
    Update a dorm
    '''
    existing_dorm = db.query(Dorm).filter(Dorm.id==dorm_id).one_or_none()
    if existing_dorm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Dorm not found')
    
    for var, value in vars(dorm).items():
        setattr(existing_dorm, var, value) if value is not None else None
    
    try:
        db.commit()
        db.refresh(existing_dorm)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    return existing_dorm