from __future__ import annotations

from textwrap import dedent
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

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


UI_HTML = dedent(
    """
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
      <meta charset=\"UTF-8\" />
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
      <title>TogetherDine Demo UI</title>
      <link rel=\"icon\" href=\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='%232563eb'/%3E%3Ctext x='50' y='63' font-size='48' text-anchor='middle' fill='white'%3ET%3C/text%3E%3C/svg%3E\" />
      <style>
        :root { color-scheme: light dark; }
        body { font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; margin: 0; background: #f5f7fa; color: #1f2937; }
        header { background: #1f2937; color: #fff; padding: 1.2rem 1.5rem; }
        header h1 { margin: 0; font-size: 1.6rem; }
        main { max-width: 1000px; margin: 0 auto; padding: 1.5rem; }
        section { background: #fff; border-radius: 10px; padding: 1rem; margin-bottom: 1.25rem; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); }
        h2 { margin-top: 0; font-size: 1.25rem; }
        form { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.85rem; align-items: end; }
        label { display: flex; flex-direction: column; font-size: 0.88rem; font-weight: 600; color: #374151; }
        input, textarea { margin-top: 0.3rem; padding: 0.55rem 0.65rem; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.95rem; background: #fff; color: inherit; }
        textarea { min-height: 80px; resize: vertical; }
        button { padding: 0.6rem 0.85rem; border-radius: 6px; border: none; font-weight: 600; cursor: pointer; }
        button.primary { background: #2563eb; color: #fff; }
        button.secondary { background: #e5e7eb; color: #1f2937; }
        button.link { background: transparent; color: #2563eb; padding-left: 0; padding-right: 0; }
        .message { display: none; margin-bottom: 1.2rem; padding: 0.85rem 1rem; border-radius: 8px; font-weight: 600; }
        .message.success { background: #d1fae5; color: #065f46; }
        .message.error { background: #fee2e2; color: #991b1b; }
        .data-output { background: #f3f4f6; border-radius: 8px; padding: 0.75rem; font-size: 0.9rem; overflow: auto; max-height: 260px; white-space: pre-wrap; }
        .slot-controls { display: flex; gap: 0.75rem; flex-wrap: wrap; }
        ul.slot-list { list-style: disc; padding-left: 1.25rem; margin: 0.75rem 0; color: #1f2937; }
        ul.slot-list li { margin-bottom: 0.35rem; }
        .intro { margin-bottom: 1rem; color: #4b5563; }
        @media (max-width: 640px) { form { grid-template-columns: 1fr; } }
      </style>
    </head>
    <body>
      <header>
        <h1>TogetherDine Demo UI</h1>
      </header>
      <main>
        <p class=\"intro\">Use these forms to manage restaurants, users, availabilities, and invitations with the TogetherDine API. Everything runs in the in-memory store, so refresh the data snapshot whenever you make changes.</p>
        <div id=\"message\" class=\"message\"></div>

        <section>
          <h2>Restaurants</h2>
          <form id=\"restaurant-form\">
            <label>Restaurant ID
              <input name=\"restaurant-id\" placeholder=\"rest-1\" required />
            </label>
            <label>Name
              <input name=\"restaurant-name\" placeholder=\"Sushi Place\" required />
            </label>
            <label>Tags (comma separated)
              <input name=\"restaurant-tags\" placeholder=\"japanese, sushi\" />
            </label>
            <label>Rating (0-5)
              <input name=\"restaurant-rating\" type=\"number\" min=\"0\" max=\"5\" step=\"0.1\" />
            </label>
            <label>Latitude
              <input name=\"restaurant-lat\" type=\"number\" step=\"0.0001\" required />
            </label>
            <label>Longitude
              <input name=\"restaurant-lon\" type=\"number\" step=\"0.0001\" required />
            </label>
            <button type=\"submit\" class=\"primary\">Create / Update Restaurant</button>
          </form>
          <div class=\"data-output\" id=\"restaurants-output\">No restaurants yet.</div>
        </section>

        <section>
          <h2>Users</h2>
          <form id=\"user-form\">
            <label>User ID
              <input name=\"user-id\" placeholder=\"alice\" required />
            </label>
            <label>Name
              <input name=\"user-name\" placeholder=\"Alice\" required />
            </label>
            <label>Wishlist restaurant IDs (comma separated)
              <input name=\"user-wishlist\" placeholder=\"rest-1, rest-2\" />
            </label>
            <label>Visited restaurant IDs (comma separated)
              <input name=\"user-visited\" placeholder=\"\" />
            </label>
            <label>Latitude
              <input name=\"user-lat\" type=\"number\" step=\"0.0001\" required />
            </label>
            <label>Longitude
              <input name=\"user-lon\" type=\"number\" step=\"0.0001\" required />
            </label>
            <button type=\"submit\" class=\"primary\">Create / Update User</button>
          </form>
          <div class=\"data-output\" id=\"users-output\">No users yet.</div>
        </section>

        <section>
          <h2>Availabilities</h2>
          <form id=\"availability-form\">
            <label>User ID
              <input name=\"availability-user\" placeholder=\"alice\" required />
            </label>
            <label>Slot start
              <input name=\"availability-start\" type=\"datetime-local\" required />
            </label>
            <label>Slot end
              <input name=\"availability-end\" type=\"datetime-local\" required />
            </label>
            <button type=\"submit\" class=\"primary\">Add Availability Slot</button>
          </form>
          <p class=\"intro\">Adding a slot retrieves existing availability for the user and appends the new window before saving.</p>
        </section>

        <section>
          <h2>Create Invitation</h2>
          <form id=\"invitation-form\">
            <label>Invitation ID
              <input name=\"inv-id\" placeholder=\"inv-1\" required />
            </label>
            <label>Organizer user ID
              <input name=\"inv-organizer\" placeholder=\"alice\" required />
            </label>
            <label>Participant IDs (comma separated)
              <input name=\"inv-participants\" placeholder=\"alice, bob\" required />
            </label>
            <label>Candidate restaurant IDs (comma separated)
              <input name=\"inv-restaurants\" placeholder=\"rest-1, rest-2\" required />
            </label>
            <label>Top options limit
              <input name=\"inv-limit\" type=\"number\" min=\"1\" max=\"10\" value=\"3\" />
            </label>
            <label>Candidate slot start
              <input id=\"inv-slot-start\" type=\"datetime-local\" />
            </label>
            <label>Candidate slot end
              <input id=\"inv-slot-end\" type=\"datetime-local\" />
            </label>
            <div class=\"slot-controls\">
              <button type=\"button\" id=\"add-slot\" class=\"secondary\">Add slot</button>
              <button type=\"button\" id=\"clear-slots\" class=\"link\">Clear slots</button>
            </div>
            <div>
              <strong>Slots:</strong>
              <ul id=\"slot-list\" class=\"slot-list\">
                <li>No slots added yet.</li>
              </ul>
            </div>
            <button type=\"submit\" class=\"primary\">Build Invitation</button>
          </form>
        </section>

        <section>
          <h2>Confirm Invitation</h2>
          <form id=\"confirm-form\">
            <label>Invitation ID
              <input name=\"confirm-invitation\" placeholder=\"inv-1\" required />
            </label>
            <label>User ID (voter)
              <input name=\"confirm-user\" placeholder=\"alice\" required />
            </label>
            <label>Option index
              <input name=\"confirm-index\" type=\"number\" min=\"0\" value=\"0\" required />
            </label>
            <button type=\"submit\" class=\"primary\">Confirm Option</button>
          </form>
        </section>

        <section>
          <h2>Data Snapshot</h2>
          <div class=\"slot-controls\">
            <button type=\"button\" id=\"refresh-data\" class=\"secondary\">Refresh snapshot</button>
          </div>
          <h3>Restaurants</h3>
          <div class=\"data-output\" id=\"restaurants-snapshot\">[]</div>
          <h3>Users</h3>
          <div class=\"data-output\" id=\"users-snapshot\">[]</div>
          <h3>Invitations</h3>
          <div class=\"data-output\" id=\"invitations-output\">[]</div>
        </section>
      </main>
      <script>
        window.addEventListener('DOMContentLoaded', () => {
          const message = document.getElementById('message');
          let messageTimer = null;

          function showMessage(type, text) {
            if (!text) { return; }
            message.textContent = text;
            message.className = `message ${type}`;
            message.style.display = 'block';
            if (messageTimer) {
              clearTimeout(messageTimer);
            }
            messageTimer = setTimeout(() => {
              message.style.display = 'none';
            }, 5000);
          }

          function clearMessage() {
            if (messageTimer) {
              clearTimeout(messageTimer);
              messageTimer = null;
            }
            message.textContent = '';
            message.style.display = 'none';
          }

          function parseCsv(value) {
            return (value || '').split(',').map(part => part.trim()).filter(Boolean);
          }

          async function apiRequest(path, { method = 'GET', body = undefined } = {}) {
            const response = await fetch(path, {
              method,
              headers: body ? { 'Content-Type': 'application/json' } : undefined,
              body: body ? JSON.stringify(body) : undefined,
            });
            let data = null;
            const text = await response.text();
            if (text) {
              try {
                data = JSON.parse(text);
              } catch (_) {
                data = text;
              }
            }
            if (!response.ok) {
              const detail = data && data.detail ? data.detail : response.statusText;
              throw new Error(detail || 'Request failed');
            }
            return data;
          }

          async function refreshRestaurants() {
            const data = await apiRequest('/restaurants');
            const target = document.getElementById('restaurants-output');
            const snapshot = document.getElementById('restaurants-snapshot');
            const formatted = JSON.stringify(data, null, 2) || '[]';
            target.textContent = formatted;
            snapshot.textContent = formatted;
          }

          async function refreshUsers() {
            const data = await apiRequest('/users');
            const target = document.getElementById('users-output');
            const snapshot = document.getElementById('users-snapshot');
            const formatted = JSON.stringify(data, null, 2) || '[]';
            target.textContent = formatted;
            snapshot.textContent = formatted;
          }

          async function refreshInvitations() {
            const data = await apiRequest('/invitations');
            const target = document.getElementById('invitations-output');
            target.textContent = JSON.stringify(data, null, 2) || '[]';
          }

          async function refreshAll() {
            try {
              await refreshRestaurants();
              await refreshUsers();
              await refreshInvitations();
            } catch (error) {
              showMessage('error', error.message);
            }
          }

          document.getElementById('restaurant-form').addEventListener('submit', async (event) => {
            event.preventDefault();
            clearMessage();
            const data = new FormData(event.target);
            const ratingValue = data.get('restaurant-rating');
            const rating = ratingValue ? Number(ratingValue) : null;
            if (ratingValue && Number.isNaN(rating)) {
              showMessage('error', 'Rating must be numeric.');
              return;
            }
            const payload = {
              id: data.get('restaurant-id'),
              name: data.get('restaurant-name'),
              tags: parseCsv(data.get('restaurant-tags')),
              rating: rating,
              latitude: Number(data.get('restaurant-lat')),
              longitude: Number(data.get('restaurant-lon')),
            };
            try {
              await apiRequest('/restaurants', { method: 'POST', body: payload });
              showMessage('success', 'Restaurant saved.');
              event.target.reset();
              await refreshRestaurants();
            } catch (error) {
              showMessage('error', `Restaurant error: ${error.message}`);
            }
          });

          document.getElementById('user-form').addEventListener('submit', async (event) => {
            event.preventDefault();
            clearMessage();
            const data = new FormData(event.target);
            const payload = {
              id: data.get('user-id'),
              name: data.get('user-name'),
              wishlist: parseCsv(data.get('user-wishlist')),
              visited: parseCsv(data.get('user-visited')),
              latitude: Number(data.get('user-lat')),
              longitude: Number(data.get('user-lon')),
            };
            try {
              await apiRequest('/users', { method: 'POST', body: payload });
              showMessage('success', 'User saved.');
              event.target.reset();
              await refreshUsers();
            } catch (error) {
              showMessage('error', `User error: ${error.message}`);
            }
          });

          document.getElementById('availability-form').addEventListener('submit', async (event) => {
            event.preventDefault();
            clearMessage();
            const data = new FormData(event.target);
            const userId = data.get('availability-user');
            const start = data.get('availability-start');
            const end = data.get('availability-end');
            if (!start || !end) {
              showMessage('error', 'Start and end must be provided.');
              return;
            }
            if (new Date(start) >= new Date(end)) {
              showMessage('error', 'Slot end must be after start.');
              return;
            }
            try {
              let existing = [];
              const response = await fetch(`/users/${encodeURIComponent(userId)}/availabilities`);
              if (response.ok) {
                existing = await response.json();
              } else if (response.status === 404) {
                existing = [];
              } else {
                const detail = await response.json().catch(() => ({}));
                const messageText = detail.detail || 'Could not fetch existing availability.';
                throw new Error(messageText);
              }
              const payload = [...existing, { slot_start: start, slot_end: end }];
              await apiRequest(`/users/${encodeURIComponent(userId)}/availabilities`, { method: 'PUT', body: payload });
              showMessage('success', 'Availability updated.');
              event.target.reset();
            } catch (error) {
              showMessage('error', `Availability error: ${error.message}`);
            }
          });

          const slotState = [];
          const slotList = document.getElementById('slot-list');

          function renderSlots() {
            if (!slotState.length) {
              slotList.innerHTML = '<li>No slots added yet.</li>';
              return;
            }
            slotList.innerHTML = slotState
              .map((slot, index) => `<li>${index + 1}. ${slot.start} → ${slot.end}</li>`)
              .join('');
          }

          document.getElementById('add-slot').addEventListener('click', () => {
            clearMessage();
            const startInput = document.getElementById('inv-slot-start');
            const endInput = document.getElementById('inv-slot-end');
            const start = startInput.value;
            const end = endInput.value;
            if (!start || !end) {
              showMessage('error', 'Provide both start and end for the slot before adding.');
              return;
            }
            if (new Date(start) >= new Date(end)) {
              showMessage('error', 'Slot end must be after start.');
              return;
            }
            slotState.push({ start, end });
            renderSlots();
            startInput.value = '';
            endInput.value = '';
          });

          document.getElementById('clear-slots').addEventListener('click', () => {
            slotState.length = 0;
            renderSlots();
          });

          document.getElementById('invitation-form').addEventListener('submit', async (event) => {
            event.preventDefault();
            clearMessage();
            if (!slotState.length) {
              showMessage('error', 'Add at least one candidate slot.');
              return;
            }
            const data = new FormData(event.target);
            const limitValue = data.get('inv-limit');
            const limit = limitValue ? Number(limitValue) : 3;
            if (Number.isNaN(limit) || limit < 1) {
              showMessage('error', 'Top limit must be a positive number.');
              return;
            }
            const payload = {
              id: data.get('inv-id'),
              organizer_id: data.get('inv-organizer'),
              participant_ids: parseCsv(data.get('inv-participants')),
              candidate_restaurant_ids: parseCsv(data.get('inv-restaurants')),
              candidate_slots: slotState.map(slot => [slot.start, slot.end]),
              top_limit: limit,
            };
            try {
              await apiRequest('/invitations', { method: 'POST', body: payload });
              showMessage('success', 'Invitation generated.');
              event.target.reset();
              slotState.length = 0;
              renderSlots();
              await refreshInvitations();
            } catch (error) {
              showMessage('error', `Invitation error: ${error.message}`);
            }
          });

          document.getElementById('confirm-form').addEventListener('submit', async (event) => {
            event.preventDefault();
            clearMessage();
            const data = new FormData(event.target);
            const invitationId = data.get('confirm-invitation');
            const optionIndex = Number(data.get('confirm-index'));
            if (Number.isNaN(optionIndex) || optionIndex < 0) {
              showMessage('error', 'Option index must be zero or a positive number.');
              return;
            }
            const payload = {
              user_id: data.get('confirm-user'),
              option_index: optionIndex,
            };
            try {
              await apiRequest(`/invitations/${encodeURIComponent(invitationId)}/confirm`, { method: 'POST', body: payload });
              showMessage('success', 'Invitation confirmed.');
              await refreshInvitations();
            } catch (error) {
              showMessage('error', `Confirm error: ${error.message}`);
            }
          });

          document.getElementById('refresh-data').addEventListener('click', () => {
            refreshAll();
          });

          refreshAll().catch(error => showMessage('error', error.message));
        });
      </script>
    </body>
    </html>
    """
)


# Health check / root endpoint ---------------------------------------------
@app.get("/")
def root() -> dict[str, str]:
    return {"message": "TogetherDine API is running"}


# GUI endpoint --------------------------------------------------------------
@app.get("/ui", response_class=HTMLResponse)
def ui() -> HTMLResponse:
    return HTMLResponse(UI_HTML)


# Favicon placeholder -------------------------------------------------------
@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> dict[str, str]:
    return {"message": "No favicon configured"}


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
