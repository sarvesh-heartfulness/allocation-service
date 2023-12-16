from fastapi import APIRouter, Depends, HTTPException, status, Query, Security
from fastapi.security import APIKeyHeader
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid

from schema import AllocationCreate, AllocationResponse, PaginatedAllocationResponse
from models import Allocation, Bed
from config.db import get_db
from deps import is_authenticated

router = APIRouter()
authorization_token = APIKeyHeader(name='Authorization', scheme_name='Authorization')
x_client_id = APIKeyHeader(name='X-Client-Id', scheme_name='X-Client-Id')

@router.get("/", response_model=PaginatedAllocationResponse, status_code=status.HTTP_200_OK)
def list_allocations(
    db: Session = Depends(get_db),
    page_size: int = Query(20, gt=0, le=100),
    page: int = Query(1, gt=0),
    bed_id: Optional[str] = Query(None),
    reg: Optional[str] = Query(None),
    partner: Optional[int] = Query(None),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
    '''
    List all the allocations
    '''
    # check for filters
    bed, reg, partner = None, None, None
    if bed_id is not None:
        bed = db.query(Bed).filter(Bed.id==bed_id).one_or_none()

    # get all the allocations
    allocations = db.query(Allocation).order_by(desc(Allocation.created_at))
    
    # apply filters if any
    if bed is not None:
        allocations = allocations.filter(Allocation.bed_id == bed_id)
    if reg is not None:
        allocations = allocations.filter(Allocation.reg_id == reg)
    if partner is not None:
        allocations = allocations.filter(Allocation.partner == partner)
    count = allocations.count()
    
    # apply pagination
    allocations = allocations.slice((page-1)*page_size, page*page_size).all()
    return {"count": count, "results": allocations}

@router.get("/{allocation_id}/", response_model=AllocationResponse, status_code=status.HTTP_200_OK)
def read_allocation(
    allocation_id: str,
    db: Session = Depends(get_db),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)
    ):
    '''
    Get an allocation by id
    '''
    # get an allocation
    allocation = db.query(Allocation).filter(Allocation.id==allocation_id).one_or_none()
    if allocation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Allocation not found')
    return allocation

@router.post("/", response_model=AllocationResponse, status_code=status.HTTP_201_CREATED)
def create_allocation(
    allocation: AllocationCreate,
    db: Session = Depends(get_db),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
    '''
    Create an allocation for a bed
    '''
    # check if bed can be allocated
    bed = db.query(Bed).filter(Bed.id==allocation.bed_id).one_or_none()
    if bed is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Bed not found')
    if not bed.active or bed.allocated or bed.blocked:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Bed cannot be allocated')
    
    # create allocation
    try:
        db_item = Allocation(**allocation.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    return db_item

@router.patch("/{allocation_id}/", response_model=AllocationResponse, status_code=status.HTTP_200_OK)
def update_allocation(
    allocation_id: uuid.UUID,
    allocation: AllocationCreate,
    db: Session = Depends(get_db),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
    '''
    Update an allocation
    '''
    # get an allocation
    existing_allocation = db.query(Allocation).filter(Allocation.id==allocation_id).one_or_none()
    if existing_allocation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Allocation not found')
    
    # check if bed can be allocated
    bed = db.query(Bed).filter(Bed.id==allocation.bed_id).one_or_none()
    if bed is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Bed not found')
    if not bed.active or bed.blocked or (bed.allocated and bed.id != existing_allocation.bed_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Bed cannot be allocated')

    # update allocation
    for var, value in vars(bed).items():
        setattr(existing_allocation, var, value) if value is not None else None
    
    try:
        db.commit()
        db.refresh(existing_allocation)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    return existing_allocation

@router.post("/bulk-allocate/", status_code=status.HTTP_200_OK)
def bulk_allocate(db: Session = Depends(get_db)):
    '''
    Bulk allocate beds
    '''
    # get all beds
    return {"message": "Beds allocated successfully!"}
