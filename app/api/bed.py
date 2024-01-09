from fastapi import APIRouter, Depends, HTTPException, status, Query, Security
from fastapi.security import APIKeyHeader
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
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
    page_size: int = Query(20, gt=0, le=200),
    page: int = Query(1, gt=0),
    only_released: Optional[bool] = Query(None),
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
    
    # check for release percentage
    if only_released and room.percent_released == 0:
        return {"count": 0, "results": []}

    # get all beds for the room in the dorm
    beds = db.query(Bed).filter(Bed.room_id==room_id)
    if only_released:
        beds = beds.order_by(asc(Bed.number))
    else:
        beds = beds.order_by(desc(Bed.created_at))
    
    # apply filters if any
    if active is not None:
        beds = beds.filter(Bed.active == active)
    
    if only_released and room.percent_released:
        # limit the beds as per release percentage 
        beds = beds.filter(Bed.active == True)
        beds_to_fetch = int(beds.count() * room.percent_released / 100)
        beds = beds.limit(beds_to_fetch)
    count = beds.count()
    
    # apply pagination if not limited by release percentage
    if not only_released:
        beds = beds.slice((page-1)*page_size, page*page_size).all()

    # get the latest allocation for each bed
    for bed in beds:
        if bed.allocations and bed.allocations[-1].active:
            bed.allocations = [bed.allocations[-1]]
        else:
            bed.allocations = []
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

    # get the latest allocation
    if bed.allocations and bed.allocations[-1].active:
        bed.allocations = [bed.allocations[-1]]
    else:
        bed.allocations = []
    return bed

@router.post("/", response_model=BedResponse, status_code=status.HTTP_201_CREATED)
def create_bed(
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
    existing_bed = db.query(Bed).filter(Bed.number==bed.number,
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

@router.patch("/{bed_id}/", response_model=BedResponse, status_code=status.HTTP_200_OK)
def update_bed(
    dorm_id: uuid.UUID,
    room_id: uuid.UUID,
    bed_id: uuid.UUID,
    bed: BedCreate,
    db: Session = Depends(get_db),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
    '''
    Update a bed
    '''
    # check if dorm and room exists
    dorm = db.query(Dorm).filter(Dorm.id==dorm_id).one_or_none()
    room = db.query(Room).filter(Room.id==room_id, Room.dorm_id==dorm_id).one_or_none()
    if dorm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Dorm not found')
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Room not found')

    # get bed
    existing_bed = db.query(Bed).filter(Bed.id==bed_id, Bed.room_id==room_id).one_or_none()
    if existing_bed is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Bed not found')
    
    # duplicate bed check
    dup_bed = db.query(Bed).filter(Bed.number==bed.number,
                                   Bed.room_id==room_id).one_or_none()
    if dup_bed is not None and dup_bed.id != bed_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Bed already exists')
    
    # update bed
    for var, value in vars(bed).items():
        setattr(existing_bed, var, value) if value is not None else None
    
    try:
        db.commit()
        db.refresh(existing_bed)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    return existing_bed