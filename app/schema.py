from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass
from models import Dorm, Room, Bed
import uuid
from datetime import datetime
from typing import Optional

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

# class RoomBase(RoomPydanticBase):
#     pass

# class RoomPydantic(RoomBase, BasePydantic):
#     pass

# class BedBase(BedPydanticBase):
#     pass

# class BedPydantic(BedBase, BasePydantic):
#     pass