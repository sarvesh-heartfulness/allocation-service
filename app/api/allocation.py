from fastapi import APIRouter, Depends, HTTPException, status, Query, Security
from fastapi.security import APIKeyHeader
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
import uuid

from schema import AllocationCreate, AllocationResponse, PaginatedAllocationResponse, \
    SoftAllocationRequest, ConfirmAllocationRequest
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
    pnr: Optional[str] = Query(None),
    is_soft_allocation: Optional[bool] = Query(None),
    active: Optional[bool] = Query(None),
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
    '''
    List all the allocations
    '''
    # get bed from bed_id
    bed = None
    if bed_id is not None:
        bed = db.query(Bed).filter(Bed.id==bed_id).one_or_none()

    # get all the allocations
    allocations = db.query(Allocation).order_by(desc(Allocation.created_at))
    
    # apply filters if any
    if bed is not None:
        allocations = allocations.filter(Allocation.bed_id == bed_id)
    if pnr is not None:
        allocations = allocations.filter(Allocation.pnr == pnr)
    if is_soft_allocation is not None:
        allocations = allocations.filter(Allocation.is_soft_allocation == is_soft_allocation)
    if active is not None:
        allocations = allocations.filter(Allocation.active == active)
    count = allocations.count()
    
    # apply pagination
    allocations = allocations.slice((page-1)*page_size, page*page_size).all()
    return {"count": count, "results": allocations}

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
    
    # check if bed is valid
    bed = db.query(Bed).filter(Bed.id==allocation.bed_id).one_or_none()
    if bed is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Bed not found')

    # update allocation
    for var, value in vars(allocation).items():
        setattr(existing_allocation, var, value) if value is not None else None
    
    try:
        db.commit()
        db.refresh(existing_allocation)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    return existing_allocation

@router.post("/soft-allocate/", status_code=status.HTTP_200_OK)
def soft_allocate(
    db: Session = Depends(get_db),
    allocations: list[SoftAllocationRequest] = None,
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
    '''
    Soft allocate beds
    '''
    # check if allocations are provided
    if not allocations:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='No allocations provided')

    # deallocate already allocated beds
    for allocation in allocations:
        existing_allocation = db.query(Allocation).filter(Allocation.pnr==allocation.pnr,
                                                          Allocation.reg==allocation.reg,
                                                          Allocation.active==True).one_or_none()
        if existing_allocation:
            existing_allocation.active = False
            bed = db.query(Bed).options(joinedload(Bed.allocations)).filter(Bed.id==existing_allocation.bed_id).one_or_none()
            if bed:
                bed.blocked = False
                bed.allocated = False
    db.commit()

    # validate allocations
    for allocation in allocations:
        bed = db.query(Bed).filter(Bed.id==allocation.bed_id).one_or_none()
        if bed is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Bed not found')
        if not bed.active or bed.blocked or bed.allocated:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f'Bed {bed.number} cannot be allocated')
    
    # soft allocate beds
    db_items = [Allocation(**allocation.model_dump(), is_soft_allocation=True) for allocation in allocations]
    db.add_all(db_items)
    db.commit()
    
    # block the soft allocated beds
    for allocation in allocations:
        bed = db.query(Bed).filter(Bed.id==allocation.bed_id).one_or_none()
        if bed:
            bed.blocked = True
    db.commit()
    
    return {"message": f'Soft locked {len(allocations)} beds successfully'}


@router.post("/confirm-soft-allocation/", status_code=status.HTTP_200_OK)
def confirm_soft_allocation(
    db: Session = Depends(get_db),
    request_data: ConfirmAllocationRequest = None,
    is_authenticated = Depends(is_authenticated),
    authorization = Security(authorization_token),
    x_client_id = Security(x_client_id)):
    '''
    Confirm soft allocated beds
    '''
    # get pnr from request
    if request_data is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='No request data provided')
    pnr = request_data.pnr
    receipt = request_data.receipt
    amount_paid = request_data.amount_paid

    # check if pnr has soft allocated beds
    allocations = db.query(Allocation).filter(Allocation.pnr==pnr,
                                              Allocation.is_soft_allocation==True,
                                              Allocation.active==True).all()
    if not allocations:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='No soft allocated beds found')
    
    # add receipt and amount paid to first allocation
    allocations[-1].receipt = receipt
    allocations[-1].amount_paid = amount_paid
    
    # confirm soft allocated beds
    allocation_ids = [allocation.id for allocation in allocations]
    db.query(Allocation).filter(Allocation.id.in_(allocation_ids)).update({Allocation.is_soft_allocation: False})

    for allocation in allocations:
        bed = db.query(Bed).filter(Bed.id==allocation.bed_id).one_or_none()
        if bed:
            bed.allocated = True
            bed.blocked = False
    db.commit()

    return {"message": f'Confirmed {len(allocations)} beds successfully.'}
