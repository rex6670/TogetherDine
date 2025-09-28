from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from math import dist
from typing import Iterable, List, Tuple

from .models import Availability, Invitation, InvitationOption, Restaurant, User
from .repository import repository


def get_users(user_ids: Iterable[str]) -> List[User]:
    users = []
    for user_id in user_ids:
        user = repository.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        users.append(user)
    return users


def get_restaurants(restaurant_ids: Iterable[str]) -> List[Restaurant]:
    restaurants = []
    for restaurant_id in restaurant_ids:
        restaurant = repository.get_restaurant(restaurant_id)
        if not restaurant:
            raise ValueError(f"Restaurant {restaurant_id} not found")
        restaurants.append(restaurant)
    return restaurants


def compute_intersection_ratio(restaurant_id: str, users: List[User]) -> float:
    interested = sum(1 for user in users if restaurant_id in user.wishlist)
    return interested / len(users) if users else 0.0


def is_user_available(user_availabilities: List[Availability], slot: Tuple[datetime, datetime]) -> bool:
    slot_start, slot_end = slot
    for availability in user_availabilities:
        if availability.slot_start <= slot_start and availability.slot_end >= slot_end:
            return True
    return False


def compute_availability_ratio(users: List[User], slot: Tuple[datetime, datetime]) -> Tuple[float, List[str]]:
    slot_start, slot_end = slot
    available_users: List[str] = []
    for user in users:
        availabilities = repository.get_availabilities(user.id)
        if is_user_available(availabilities, (slot_start, slot_end)):
            available_users.append(user.id)
    ratio = len(available_users) / len(users) if users else 0.0
    return ratio, available_users


def compute_convenience_score(restaurant: Restaurant, users: List[User]) -> float:
    if not users:
        return 0.0
    distances = [
        dist((user.latitude, user.longitude), (restaurant.latitude, restaurant.longitude))
        for user in users
    ]
    if not distances:
        return 0.0
    # Lower distance should yield a higher score. Normalize using inverse distance.
    # Add a small epsilon to avoid division by zero.
    epsilon = 1e-6
    inverted = [1 / (d + epsilon) for d in distances]
    return sum(inverted) / len(inverted)


def score_option(
    restaurant: Restaurant,
    slot: Tuple[datetime, datetime],
    users: List[User],
) -> InvitationOption:
    intersection_ratio = compute_intersection_ratio(restaurant.id, users)
    availability_ratio, available_users = compute_availability_ratio(users, slot)
    convenience_score = compute_convenience_score(restaurant, users)
    total_score = intersection_ratio + availability_ratio + convenience_score
    return InvitationOption(
        restaurant_id=restaurant.id,
        slot_start=slot[0],
        slot_end=slot[1],
        participants=available_users,
        intersection_ratio=intersection_ratio,
        availability_ratio=availability_ratio,
        convenience_score=convenience_score,
        total_score=total_score,
    )


def generate_top_options(invitation: Invitation, limit: int = 3) -> List[InvitationOption]:
    users = get_users(invitation.participant_ids)
    restaurants = get_restaurants(invitation.candidate_restaurant_ids)

    options: List[InvitationOption] = []
    for restaurant in restaurants:
        for slot in invitation.candidate_slots:
            options.append(score_option(restaurant, slot, users))
    options.sort(key=lambda option: option.total_score, reverse=True)
    return options[:limit]


def build_invitation(
    invitation: Invitation,
    limit: int = 3,
) -> Invitation:
    top_options = generate_top_options(invitation, limit=limit)
    invitation = replace(invitation, top_options=top_options)
    repository.add_invitation(invitation)
    return invitation


def confirm_option(invitation_id: str, option_index: int) -> Invitation:
    invitation = repository.get_invitation(invitation_id)
    if not invitation:
        raise ValueError("Invitation not found")
    if not (0 <= option_index < len(invitation.top_options)):
        raise ValueError("Invalid option index")
    option = invitation.top_options[option_index]
    calendar_link = f"https://calendar.example.com/events/{invitation_id}-{option_index}"
    reservation_link = f"https://reservations.example.com/{option.restaurant_id}?slot={option.slot_start.isoformat()}"
    invitation.confirmed_option = option
    invitation.calendar_link = calendar_link
    invitation.reservation_link = reservation_link
    repository.add_invitation(invitation)
    return invitation
