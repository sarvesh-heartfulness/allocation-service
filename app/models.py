from enum import Enum
from sqlalchemy import Boolean, Column, event, ForeignKey, Integer, JSON, String, VARCHAR, Text, DateTime
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

    class DORM_TYPES(str, Enum):
        EAST_BUNK_BED = 'east_bunk_bed'
        NORTH_GROUND_FLOOR_WOODEN_BED = 'north_ground_floor_wooden_bed'
        SOUTH_BUNK_BED = 'south_bunk_bed'

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    class AMOUNT_FOR_TYPES(str, Enum):
        EVENT = 'event'
        DAY = 'day'

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True, unique=True)
    type = Column(types.Enum(*[i[0] for i in DORM_TYPES.choices()], name="type"), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Integer, nullable=False)
    amount_for = Column(types.Enum(*[i[0] for i in AMOUNT_FOR_TYPES.choices()], name="amount_type"), nullable=False)
    active = Column(Boolean, default=True)

    # relationships
    rooms = relationship("Room", back_populates="dorm")

class Room(BaseModel):
    __tablename__ = "room"

    class FLOORS(str, Enum):
        GF = 'gf'
        FF = 'ff'

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
    max_count = Column(Integer, default=0)
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
    name = Column(String, nullable=False, index=True)
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
