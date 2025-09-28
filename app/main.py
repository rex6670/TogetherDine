from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException

from . import services
from .models import Availability, Invitation, InvitationOption, Restaurant, User
from .repository import repository
from .schemas import (
    AvailabilityCreate,
    AvailabilityRead,
    InvitationCreate,
    InvitationOptionRead,
    InvitationRead,
    RestaurantCreate,
    RestaurantRead,
    UserCreate,
    UserRead,
    VoteCreate,
)

app = FastAPI(title="TogetherDine API", version="0.1.0")


# Restaurant endpoints -----------------------------------------------------
@app.post("/restaurants", response_model=RestaurantRead)
def create_restaurant(payload: RestaurantCreate) -> RestaurantRead:
    restaurant = Restaurant(**payload.dict())
    repository.add_restaurant(restaurant)
    return RestaurantRead(**payload.dict())


@app.get("/restaurants", response_model=List[RestaurantRead])
def list_restaurants() -> List[RestaurantRead]:
    return [RestaurantRead(**restaurant.__dict__) for restaurant in repository.list_restaurants()]


# User endpoints -----------------------------------------------------------
@app.post("/users", response_model=UserRead)
def create_user(payload: UserCreate) -> UserRead:
    user = User(
        id=payload.id,
        name=payload.name,
        wishlist=set(payload.wishlist),
        visited=set(payload.visited),
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    repository.add_user(user)
    return serialize_user(user)


@app.get("/users", response_model=List[UserRead])
def list_users() -> List[UserRead]:
    return [serialize_user(user) for user in repository.list_users()]


def serialize_user(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        name=user.name,
        wishlist=sorted(user.wishlist),
        visited=sorted(user.visited),
        latitude=user.latitude,
        longitude=user.longitude,
    )


# Availability endpoints ---------------------------------------------------
@app.put("/users/{user_id}/availabilities", response_model=List[AvailabilityRead])
def set_availabilities(user_id: str, payload: List[AvailabilityCreate]) -> List[AvailabilityRead]:
    if not repository.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    availabilities = [
        Availability(user_id=user_id, slot_start=item.slot_start, slot_end=item.slot_end)
        for item in payload
    ]
    repository.set_availabilities(user_id, availabilities)
    return [AvailabilityRead(**item.__dict__) for item in availabilities]


@app.get("/users/{user_id}/availabilities", response_model=List[AvailabilityRead])
def get_availabilities(user_id: str) -> List[AvailabilityRead]:
    if not repository.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    availabilities = repository.get_availabilities(user_id)
    return [AvailabilityRead(**item.__dict__) for item in availabilities]


# Invitation endpoints -----------------------------------------------------
@app.post("/invitations", response_model=InvitationRead)
def create_invitation(payload: InvitationCreate) -> InvitationRead:
    try:
        candidate_slots = [(slot[0], slot[1]) for slot in payload.candidate_slots]
        invitation = Invitation(
            id=payload.id,
            organizer_id=payload.organizer_id,
            participant_ids=payload.participant_ids,
            candidate_restaurant_ids=payload.candidate_restaurant_ids,
            candidate_slots=candidate_slots,
        )
        invitation = services.build_invitation(invitation, limit=payload.top_limit)
        return serialize_invitation(invitation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/invitations/{invitation_id}/confirm", response_model=InvitationRead)
def confirm_invitation(invitation_id: str, payload: VoteCreate) -> InvitationRead:
    try:
        invitation = services.confirm_option(invitation_id, payload.option_index)
        return serialize_invitation(invitation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/invitations", response_model=List[InvitationRead])
def list_invitations() -> List[InvitationRead]:
    return [serialize_invitation(invitation) for invitation in repository.list_invitations()]


def serialize_invitation(invitation: Invitation) -> InvitationRead:
    return InvitationRead(
        id=invitation.id,
        organizer_id=invitation.organizer_id,
        participant_ids=invitation.participant_ids,
        candidate_restaurant_ids=invitation.candidate_restaurant_ids,
        candidate_slots=[[slot[0], slot[1]] for slot in invitation.candidate_slots],
        top_options=[serialize_option(option) for option in invitation.top_options],
        confirmed_option=serialize_option(invitation.confirmed_option),
        calendar_link=invitation.calendar_link,
        reservation_link=invitation.reservation_link,
    )


def serialize_option(option: Optional[InvitationOption]) -> Optional[InvitationOptionRead]:
    if option is None:
        return None
    return InvitationOptionRead(
        restaurant_id=option.restaurant_id,
        slot_start=option.slot_start,
        slot_end=option.slot_end,
        participants=option.participants,
        intersection_ratio=option.intersection_ratio,
        availability_ratio=option.availability_ratio,
        convenience_score=option.convenience_score,
        total_score=option.total_score,
    )
