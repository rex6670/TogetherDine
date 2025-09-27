from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from .models import Availability, CalendarEvent, Invitation, Restaurant, User, Vote


class InMemoryRepository:
    """A naive in-memory repository backing the MVP endpoints."""

    def __init__(self) -> None:
        self.restaurants: Dict[str, Restaurant] = {}
        self.users: Dict[str, User] = {}
        self.availabilities: Dict[str, List[Availability]] = defaultdict(list)
        self.invitations: Dict[str, Invitation] = {}
        self.calendar_events: Dict[str, CalendarEvent] = {}
        self.votes: Dict[str, Dict[str, Vote]] = defaultdict(dict)

    # Restaurant CRUD -----------------------------------------------------
    def add_restaurant(self, restaurant: Restaurant) -> None:
        self.restaurants[restaurant.id] = restaurant

    def get_restaurant(self, restaurant_id: str) -> Optional[Restaurant]:
        return self.restaurants.get(restaurant_id)

    def list_restaurants(self) -> List[Restaurant]:
        return list(self.restaurants.values())

    # User CRUD -----------------------------------------------------------
    def add_user(self, user: User) -> None:
        self.users[user.id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def list_users(self) -> List[User]:
        return list(self.users.values())

    # Availability --------------------------------------------------------
    def set_availabilities(self, user_id: str, availabilities: Iterable[Availability]) -> None:
        self.availabilities[user_id] = list(availabilities)

    def get_availabilities(self, user_id: str) -> List[Availability]:
        return self.availabilities.get(user_id, [])

    # Invitation ----------------------------------------------------------
    def add_invitation(self, invitation: Invitation) -> None:
        self.invitations[invitation.id] = invitation

    def get_invitation(self, invitation_id: str) -> Optional[Invitation]:
        return self.invitations.get(invitation_id)

    def list_invitations(self) -> List[Invitation]:
        return list(self.invitations.values())

    def save_calendar_event(self, event: CalendarEvent) -> None:
        self.calendar_events[event.invitation_id] = event

    def get_calendar_event(self, invitation_id: str) -> Optional[CalendarEvent]:
        return self.calendar_events.get(invitation_id)

    # Voting --------------------------------------------------------------
    def record_vote(self, vote: Vote) -> None:
        self.votes[vote.invitation_id][vote.user_id] = vote

    def get_votes(self, invitation_id: str) -> Dict[str, Vote]:
        return self.votes.get(invitation_id, {})


repository = InMemoryRepository()
