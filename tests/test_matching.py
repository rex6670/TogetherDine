from datetime import datetime, timedelta

from app import services
from app.models import Availability, Invitation, Restaurant, User
from app.repository import repository


def setup_function() -> None:
    repository.restaurants.clear()
    repository.users.clear()
    repository.availabilities.clear()
    repository.invitations.clear()
    repository.calendar_events.clear()
    repository.votes.clear()


def create_user(user_id: str, wishlist: list[str], location: tuple[float, float]) -> None:
    user = User(
        id=user_id,
        name=user_id,
        wishlist=set(wishlist),
        visited=set(),
        latitude=location[0],
        longitude=location[1],
    )
    repository.add_user(user)


def create_restaurant(restaurant_id: str, location: tuple[float, float]) -> None:
    restaurant = Restaurant(
        id=restaurant_id,
        name=restaurant_id,
        tags=["asian"],
        rating=4.5,
        latitude=location[0],
        longitude=location[1],
    )
    repository.add_restaurant(restaurant)


def test_generate_top_options_prioritizes_high_scores() -> None:
    now = datetime.utcnow()
    slot_a = (now + timedelta(days=1), now + timedelta(days=1, hours=2))
    slot_b = (now + timedelta(days=2), now + timedelta(days=2, hours=2))

    create_user("alice", ["sushi", "ramen"], (0.0, 0.0))
    create_user("bob", ["sushi"], (0.0, 0.1))
    create_user("carol", ["ramen"], (0.0, -0.1))

    for user_id, slot in [("alice", slot_a), ("bob", slot_a), ("carol", slot_b)]:
        repository.set_availabilities(
            user_id,
            [Availability(user_id=user_id, slot_start=slot[0], slot_end=slot[1])],
        )

    create_restaurant("sushi", (0.0, 0.0))
    create_restaurant("ramen", (1.0, 1.0))

    invitation = Invitation(
        id="inv-1",
        organizer_id="alice",
        participant_ids=["alice", "bob", "carol"],
        candidate_restaurant_ids=["sushi", "ramen"],
        candidate_slots=[slot_a, slot_b],
    )

    result = services.generate_top_options(invitation)

    assert result, "No options generated"
    assert result[0].restaurant_id == "sushi"
    assert result[0].participants == ["alice", "bob"]


def test_confirm_option_sets_calendar_links() -> None:
    now = datetime.utcnow()
    slot = (now + timedelta(days=1), now + timedelta(days=1, hours=2))
    create_user("host", ["bbq"], (0.0, 0.0))
    repository.set_availabilities(
        "host",
        [Availability(user_id="host", slot_start=slot[0], slot_end=slot[1])],
    )
    create_restaurant("bbq", (0.0, 0.0))

    invitation = Invitation(
        id="inv-2",
        organizer_id="host",
        participant_ids=["host"],
        candidate_restaurant_ids=["bbq"],
        candidate_slots=[slot],
    )
    invitation = services.build_invitation(invitation)

    confirmed = services.confirm_option("inv-2", 0)

    assert confirmed.confirmed_option is not None
    assert confirmed.calendar_link is not None
    assert confirmed.reservation_link is not None
