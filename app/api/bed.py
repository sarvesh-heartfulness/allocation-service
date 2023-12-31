from fastapi import APIRouter, Depends, HTTPException, status, Query, Security
from fastapi.security import APIKeyHeader
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uuid

from schema import BedCreate, BedResponse, PaginatedBedResponse
from models import Bed, Dorm, Room
from config.db import get_db
from deps import is_authenticated

router = APIRouter()
authorization_token = APIKeyHeader(name='Authorization', scheme_name='Authorization')
x_client_id = APIKeyHeader(name='X-Client-Id', scheme_name='X-Client-Id')

@router.get("/", response_model=PaginatedBedResponse, status_code=status.HTTP_200_OK)
def list_beds(
    dorm_id: str,
    room_id: str,
    db: Session = Depends(get_db),
    page_size: int = Query(20, gt=0, le=100),
    page: int = Query(1, gt=0),
    active: Optional[bool] = Query(None),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
    '''
    List all the beds for a room in a dorm
    '''
    # check if dorm and room exists
    dorm = db.query(Dorm).filter(Dorm.id==dorm_id).one_or_none()
    room = db.query(Room).filter(Room.id==room_id, Room.dorm_id==dorm_id).one_or_none()
    if dorm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Dorm not found')
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Room not found')

    # get all beds for the room in the dorm
    beds = db.query(Bed).filter(Bed.room_id==room_id).order_by(desc(Bed.created_at))
    count = beds.count()
    
    # apply filters if any
    if active is not None:
        beds = beds.filter(Bed.active == active)
    
    # apply pagination
    beds = beds.slice((page-1)*page_size, page*page_size).all()
    return {"count": count, "results": beds}

@router.get("/{bed_id}/", response_model=BedResponse, status_code=status.HTTP_200_OK)
def read_bed(
    dorm_id: str,
    room_id: str,
    bed_id: str,
    db: Session = Depends(get_db),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)
    ):
    '''
    Get a bed by id
    '''
    # check if dorm and room exists
    dorm = db.query(Dorm).filter(Dorm.id==dorm_id).one_or_none()
    room = db.query(Room).filter(Room.id==room_id, Room.dorm_id==dorm_id).one_or_none()
    if dorm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Dorm not found')
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Room not found')

    # get a bed
    bed = db.query(Bed).filter(Bed.id==bed_id, Bed.room_id==room_id).one_or_none()
    if bed is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Bed not found')
    return bed

@router.post("/", response_model=BedResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    dorm_id: uuid.UUID,
    room_id: uuid.UUID,
    bed: BedCreate,
    db: Session = Depends(get_db),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
    '''
    Create new bed for a room in a dorm
    '''
    # check if dorm exists
    dorm = db.query(Dorm).filter(Dorm.id==dorm_id).one_or_none()
    room = db.query(Room).filter(Room.id==room_id, Room.dorm_id==dorm_id).one_or_none()
    if dorm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Dorm not found')
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Room not found')
    
    # check if bed already exists
    existing_bed = db.query(Bed).filter(Bed.name==bed.name,
                                        Bed.room_id==room_id).one_or_none()
    if existing_bed is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Bed already exists')

    # create bed
    try:
        db_item = Bed(**bed.model_dump(), room_id=room_id)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str('Bed already exists'))
    return db_item
