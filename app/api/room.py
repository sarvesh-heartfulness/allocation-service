from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uuid

from schema import RoomCreate, RoomResponse, DormPydanticRead
from models import Dorm, Room
from config.db import get_db

router = APIRouter()

@router.get("/", response_model=List[RoomResponse], status_code=status.HTTP_200_OK)
def list_rooms_for_a_dorm(
    dorm_id: str,
    db: Session = Depends(get_db),
    limit: int = 20,
    skip: int = 0,
    active: Optional[bool] = Query(None),):
    '''
    List all the rooms for a dorm
    '''
    # check if dorm exists
    dorm = db.query(Dorm).filter(Dorm.id==dorm_id).one_or_none()
    if dorm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Dorm not found')

    # get all rooms for this dorm
    rooms = db.query(Room).filter(Room.dorm_id==dorm_id).order_by(desc(Room.created_at))
    
    # apply filters if any
    if active is not None:
        rooms = rooms.filter(Room.active == active)
    
    # apply pagination
    rooms = rooms.offset(skip).limit(limit).all()
    return rooms

@router.get("/{room_id}/", response_model=RoomResponse, status_code=status.HTTP_200_OK)
def read_room(
    dorm_id: str,
    room_id: str,
    db: Session = Depends(get_db)):
    '''
    Get a room by id
    '''
    # check if dorm exists
    dorm = db.query(Dorm).filter(Dorm.id==dorm_id).one_or_none()
    if dorm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Dorm not found')

    # get room
    room = db.query(Room).filter(Room.id==room_id).one_or_none()
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Room not found')
    return room

@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    dorm_id: uuid.UUID,
    room: RoomCreate,
    db: Session = Depends(get_db)):
    '''
    Create new room for a dorm
    '''
    # check if dorm exists
    dorm = db.query(Dorm).filter(Dorm.id==dorm_id).one_or_none()
    if dorm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Dorm not found')
    
    # check if room already exists
    existing_room = db.query(Room).filter(Room.name==room.name,
                                          Room.dorm_id==dorm_id).one_or_none()
    if existing_room is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Room already exists')

    # create room
    try:
        db_item = Room(**room.model_dump(), dorm_id=dorm_id)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str('Room already exists'))
    return db_item

@router.patch("/{room_id}/", response_model=RoomResponse, status_code=status.HTTP_200_OK)
def update_room(
    dorm_id: uuid.UUID,
    room_id: uuid.UUID,
    room: RoomCreate,
    db: Session = Depends(get_db)):
    '''
    Update a room
    '''
    # check if dorm exists
    dorm = db.query(Dorm).filter(Dorm.id==dorm_id).one_or_none()
    if dorm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Dorm not found')

    # check if room exists
    existing_room = db.query(Room).filter(Room.id==room_id).one_or_none()
    if existing_room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Room not found')
    
    # check if room already exists
    dup_room = db.query(Room).filter(Room.name==room.name,
                                          Room.dorm_id==dorm_id).one_or_none()
    if dup_room is not None and dup_room.id != room_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Room already exists')
    
    # update room
    for var, value in vars(room).items():
        setattr(existing_room, var, value) if value else None
    
    try:
        db.commit()
        db.refresh(existing_room)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    return existing_room