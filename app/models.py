from enum import Enum
from sqlalchemy import Boolean, Column, event, Float, ForeignKey, Integer, JSON, String, VARCHAR, Text, DateTime
from sqlalchemy import types
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from config.db import Base

class BaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Dorm(BaseModel):
    __tablename__ = "dorm"

    class AMOUNT_FOR_TYPES(str, Enum):
        EVENT = 'event'
        DAY = 'day'

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True, unique=True)
    description = Column(Text, nullable=True)
    amount = Column(Integer, nullable=False)
    amount_for = Column(types.Enum(*[i[0] for i in AMOUNT_FOR_TYPES.choices()], name="amount_type"), nullable=False)
    active = Column(Boolean, default=True)

    # relationships
    rooms = relationship("Room", back_populates="dorm")

class Room(BaseModel):
    __tablename__ = "room"

    class FLOORS(str, Enum):
        GF = 'gf' # ground floor
        FF = 'ff' # first floor
        SF = 'sf' # second floor
        TF = 'tf' # third floor

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    class BED_TYPES(str, Enum):
        BUNK = 'bunk'
        METAL = 'metal'
        WOOD = 'wood'

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    class PARTICIPANT_TYPES(str, Enum):
        GENERAL = 'general'
        SISTERS_ONLY = 'sisters_only'
        OVERSEAS_ONLY = 'overseas_only'

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]
        
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    dorm_id = Column(UUID, ForeignKey(Dorm.id), nullable=False)
    room_identifier = Column(Integer, nullable=False)
    ac_available = Column(Boolean, default=False)
    floor = Column(types.Enum(*[i[0] for i in FLOORS.choices()], name="floor"), nullable=False)
    close_to_dorm_entrance = Column(Boolean, default=False)
    close_to_bath = Column(Boolean, default=False)
    percent_released = Column(Integer)
    bed_type = Column(types.Enum(*[i[0] for i in BED_TYPES.choices()], name="bed_type"), nullable=False)
    is_multibatch = Column(Boolean, default=False)
    participant_type = Column(types.Enum(*[i[0] for i in PARTICIPANT_TYPES.choices()], name="participant_type"), nullable=False)
    reset_allowed = Column(Boolean, default=False)
    active = Column(Boolean, default=True)

    # relationships
    dorm = relationship("Dorm", back_populates="rooms")
    beds = relationship("Bed", back_populates="room")

class Bed(BaseModel):
    __tablename__ = "bed"

    class LEVELS(str, Enum):
        LOWER = 'lower'
        UPPER = 'upper'

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]
        
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    room_id = Column(UUID, ForeignKey(Room.id), nullable=False)
    number = Column(Integer)
    blocked = Column(Boolean, default=False)
    level = Column(types.Enum(*[i[0] for i in LEVELS.choices()], name="level"), nullable=False)
    close_to_dorm_entrance = Column(Boolean, default=False)
    close_to_bath = Column(Boolean, default=False)
    allocated = Column(Boolean, default=False)
    active = Column(Boolean, default=True)

    # relationships
    room = relationship("Room", back_populates="beds")
    allocations = relationship("Allocation", back_populates="bed")

class Allocation(BaseModel):
    __tablename__ = "allocation"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    bed_id = Column(UUID, ForeignKey(Bed.id), nullable=False)
    pnr = Column(String, nullable=True, index=True)
    reg = Column(String, nullable=True, index=True)
    partner = Column(Integer, nullable=True, index=True)
    name = Column(String, nullable=True)
    is_soft_allocation = Column(Boolean, default=False)
    receipt = Column(String, nullable=True)
    amount_paid = Column(Float, nullable=True)
    checkin_date = Column(DateTime, nullable=True)
    checkout_date = Column(DateTime, nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    # relationships
    bed = relationship("Bed", back_populates="allocations")
