from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Sequence

from pydantic import BaseModel, Field, validator


class RestaurantCreate(BaseModel):
    id: str = Field(..., description="Unique identifier for the restaurant")
    name: str
    tags: List[str] = Field(default_factory=list)
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    latitude: float
    longitude: float


class RestaurantRead(RestaurantCreate):
    pass


class UserCreate(BaseModel):
    id: str
    name: str
    wishlist: List[str] = Field(default_factory=list)
    visited: List[str] = Field(default_factory=list)
    latitude: float = 0.0
    longitude: float = 0.0


class UserRead(UserCreate):
    pass


class AvailabilityCreate(BaseModel):
    slot_start: datetime
    slot_end: datetime

    @validator("slot_end")
    def validate_end_after_start(cls, v: datetime, values: dict) -> datetime:
        slot_start: datetime = values.get("slot_start")
        if slot_start and v <= slot_start:
            raise ValueError("slot_end must be after slot_start")
        return v


class AvailabilityRead(AvailabilityCreate):
    pass


class InvitationCreate(BaseModel):
    id: str
    organizer_id: str
    participant_ids: List[str]
    candidate_restaurant_ids: List[str]
    candidate_slots: List[List[datetime]] = Field(..., description="Pairs of ISO start/end datetimes")
    top_limit: int = 3

    @validator("candidate_slots")
    def validate_slots(cls, slots: Sequence[Sequence[datetime]]) -> List[List[datetime]]:
        if not slots:
            raise ValueError("candidate_slots must not be empty")
        validated: List[List[datetime]] = []
        for slot in slots:
            if len(slot) != 2:
                raise ValueError("Each slot must contain a [start, end] pair")
            start, end = slot
            if end <= start:
                raise ValueError("Slot end must be after start")
            validated.append([start, end])
        return validated


class InvitationOptionRead(BaseModel):
    restaurant_id: str
    slot_start: datetime
    slot_end: datetime
    participants: List[str]
    intersection_ratio: float
    availability_ratio: float
    convenience_score: float
    total_score: float


class InvitationRead(BaseModel):
    id: str
    organizer_id: str
    participant_ids: List[str]
    candidate_restaurant_ids: List[str]
    candidate_slots: List[List[datetime]]
    top_options: List[InvitationOptionRead]
    confirmed_option: Optional[InvitationOptionRead] = None
    calendar_link: Optional[str] = None
    reservation_link: Optional[str] = None


class VoteCreate(BaseModel):
    user_id: str
    option_index: int


class VoteRead(VoteCreate):
    pass
