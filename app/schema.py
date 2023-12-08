from pydantic import BaseModel, Field
from pydantic._internal._model_construction import ModelMetaclass
from models import Dorm, Room, Bed
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
    type: Dorm.DORM_TYPES
    description: str = None
    amount: int
    amount_for: Dorm.AMOUNT_FOR_TYPES
    active: bool = True

class DormPydanticWrite(BasePydantic):
    name: str
    type: Dorm.DORM_TYPES
    description: str = None
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
    max_count: int = Field(0, title="Max Count", description="Max Count")
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
    max_count: int
    participant_type: Room.PARTICIPANT_TYPES
    reset_allowed: bool
    active: bool

class PaginatedRoomResponse(BaseModel):
    count: int
    results: List[RoomResponse]

class BedCreate(BaseModel):
    name: str = Field(..., title="Bed Name", description="Name of the bed")
    number: int = Field(..., title="Number", description="Number")
    blocked: bool = Field(False, title="Blocked", description="Blocked")
    level: Bed.LEVELS = Field(..., title="Level", description="Level")
    close_to_dorm_entrance: bool = Field(False, title="Close to Dorm Entrance", description="Close to Dorm Entrance")
    close_to_bath: bool = Field(False, title="Close to Bath", description="Close to Bath")
    allocated: bool = Field(False, title="Allocated", description="Allocated")
    active: bool = Field(True, title="Active", description="Active")

class BedResponse(ReadOnly):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    room_id: uuid.UUID
    name: str
    number: int
    blocked: bool
    level: Bed.LEVELS
    close_to_dorm_entrance: bool
    close_to_bath: bool
    allocated: bool
    active: bool

class PaginatedBedResponse(BaseModel):
    count: int
    results: List[BedResponse]