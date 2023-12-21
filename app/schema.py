from pydantic import BaseModel, Field
from pydantic._internal._model_construction import ModelMetaclass
from models import Allocation, Bed, Dorm, Room
import uuid
from datetime import datetime
from typing import Optional, List

class BasePydantic(BaseModel):
    class Config:
        from_attributes = True

class AllOptional(ModelMetaclass):
    def __new__(mcls, name, bases, namespaces, **kwargs):
        cls = super().__new__(mcls, name, bases, namespaces, **kwargs)
        for field in cls.__fields__.values():
            if getattr(field, "required", False):
                field.required=False
        return cls

# Dorm schema
# class DormBase(DormPydanticBase):
#     pass

class DormPydanticRead(BasePydantic):
    id: Optional[uuid.UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    name: str
    description: str | None
    amount: int
    amount_for: Dorm.AMOUNT_FOR_TYPES
    active: bool = True

class DormPydanticWrite(BasePydantic):
    name: str
    description: str = Field('', title="Description", description="Description of the dorm")
    amount: int
    amount_for: Dorm.AMOUNT_FOR_TYPES
    active: bool = True

class DormPydanticUpdate(DormPydanticWrite, metaclass=AllOptional):
    pass

class PaginatedDormResponse(BaseModel):
    count: int
    results: List[DormPydanticRead]

# class RoomBase(RoomPydanticBase):
#     pass

# class RoomPydantic(RoomBase, BasePydantic):
#     pass

# class BedBase(BedPydanticBase):
#     pass

# class BedPydantic(BedBase, BasePydantic):
#     pass

class ReadOnly(BaseModel):
    class Config:
        allow_mutation = False

class RoomCreate(BaseModel):
    name: str = Field(..., title="Room Name", description="Name of the room")
    room_identifier: int = Field(..., title="Room Identifier", description="Room identifier")
    ac_available: bool = Field(False, title="AC Available", description="AC Available")
    floor: Room.FLOORS = Field(..., title="Floor", description="Floor")
    close_to_dorm_entrance: bool = Field(False, title="Close to Dorm Entrance", description="Close to Dorm Entrance")
    close_to_bath: bool = Field(False, title="Close to Bath", description="Close to Bath")
    percent_released: int = Field(None, title="Percent Released", description="Percent Released")
    bed_type: Room.BED_TYPES = Field(..., title="Bed Type", description="Bed Type")
    is_multibatch: bool = Field(False, title="Is Multibatch", description="Is Multibatch")
    participant_type: Room.PARTICIPANT_TYPES = Field(..., title="Participant Type", description="Participant Type")
    reset_allowed: bool = Field(False, title="Reset Allowed", description="Reset Allowed")
    active: bool = Field(True, title="Active", description="Active")

class RoomResponse(ReadOnly):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    dorm_id: uuid.UUID
    name: str
    room_identifier: int
    ac_available: bool
    floor: Room.FLOORS
    close_to_dorm_entrance: bool
    close_to_bath: bool
    percent_released: int
    bed_type: Room.BED_TYPES
    is_multibatch: bool
    participant_type: Room.PARTICIPANT_TYPES
    reset_allowed: bool
    active: bool

class PaginatedRoomResponse(BaseModel):
    count: int
    results: List[RoomResponse]

class BedCreate(BaseModel):
    number: int = Field(0, title="Number", description="Number")
    blocked: bool = Field(False, title="Blocked", description="Blocked")
    level: Bed.LEVELS = Field(..., title="Level", description="Level")
    close_to_dorm_entrance: bool = Field(False, title="Close to Dorm Entrance", description="Close to Dorm Entrance")
    close_to_bath: bool = Field(False, title="Close to Bath", description="Close to Bath")
    allocated: bool = Field(False, title="Allocated", description="Allocated")
    active: bool = Field(True, title="Active", description="Active")

class BedAllocationResponse(ReadOnly):
    id: uuid.UUID
    pnr: str | None
    reg: str | None
    name: str | None
    is_soft_allocation: bool

class BedResponse(ReadOnly):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    room_id: uuid.UUID
    number: int | None
    blocked: bool
    level: Bed.LEVELS
    close_to_dorm_entrance: bool
    close_to_bath: bool
    allocated: bool
    allocations: List[BedAllocationResponse]
    active: bool

class PaginatedBedResponse(BaseModel):
    count: int
    results: List[BedResponse]

class AllocationCreate(BaseModel):
    bed_id: uuid.UUID
    pnr: str = Field(None, title="PNR", description="PNR")
    reg: str = Field(None, title="Registration ID", description="Registration ID")
    partner: int = Field(None, title="Partner ID", description="Partner ID")
    name: str = Field(None, title="Name", description="Name of the participant")
    is_soft_allocation: bool = Field(False, title="Is Soft Allocation", description="Is Soft Allocation")
    receipt: str = Field(None, title="Receipt", description="Receipt")
    amount_paid: float = Field(None, title="Amount Paid", description="Amount Paid")
    checkin_date: datetime = Field(None, title="Checkin Date", description="Checkin Date")
    checkout_date: datetime = Field(None, title="Checkout Date", description="Checkout Date")

class AllocationResponse(ReadOnly):
    id: uuid.UUID
    created_at: datetime | None
    updated_at: datetime | None
    bed_id: uuid.UUID
    pnr: str | None
    reg: str | None
    partner: int | None
    name: str | None
    is_soft_allocation: bool
    receipt: str | None
    amount_paid: float | None
    checkin_date: datetime | None
    checkout_date: datetime | None

class PaginatedAllocationResponse(BaseModel):
    count: int
    results: List[AllocationResponse]

class SoftAllocationRequest(BaseModel):
    bed_id: uuid.UUID
    pnr: str = Field(..., title="PNR", description="PNR")
    reg: str = Field(..., title="Registration ID", description="Registration ID")
    partner: int = Field(None, title="Partner ID", description="Partner ID")
    name: str = Field(None, title="Name", description="Name of the participant")
    receipt: str = Field(None, title="Receipt", description="Receipt")
    amount_paid: float = Field(None, title="Amount Paid", description="Amount Paid")
    checkin_date: datetime = Field(None, title="Checkin Date", description="Checkin Date")
    checkout_date: datetime = Field(None, title="Checkout Date", description="Checkout Date")

class ConfirmAllocationRequest(BaseModel):
    pnr: str
    receipt: str = Field('', title="Receipt", description="Receipt")
    amount_paid: float = Field(0.0, title="Amount Paid", description="Amount Paid")
