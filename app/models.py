from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set


@dataclass
class Restaurant:
    id: str
    name: str
    tags: List[str]
    rating: Optional[float]
    latitude: float
    longitude: float


@dataclass
class User:
    id: str
    name: str
    wishlist: Set[str] = field(default_factory=set)
    visited: Set[str] = field(default_factory=set)
    latitude: float = 0.0
    longitude: float = 0.0


@dataclass
class Availability:
    user_id: str
    slot_start: datetime
    slot_end: datetime


@dataclass
class InvitationOption:
    restaurant_id: str
    slot_start: datetime
    slot_end: datetime
    participants: List[str]
    intersection_ratio: float
    availability_ratio: float
    convenience_score: float
    total_score: float


@dataclass
class Invitation:
    id: str
    organizer_id: str
    participant_ids: List[str]
    candidate_restaurant_ids: List[str]
    candidate_slots: List[tuple[datetime, datetime]]
    top_options: List[InvitationOption] = field(default_factory=list)
    confirmed_option: Optional[InvitationOption] = None
    calendar_link: Optional[str] = None
    reservation_link: Optional[str] = None


@dataclass
class CalendarEvent:
    invitation_id: str
    option: InvitationOption
    url: str


@dataclass
class Vote:
    invitation_id: str
    user_id: str
    option_key: str
