# ChatDash - Real-Time Chat Application

A full-stack real-time chat application built with Django + Channels (backend) and React + Vite (frontend). Supports direct messages, group rooms, online presence, message editing/deletion, and typing indicators — all over WebSocket.

## Tech Stack

**Backend**
- Django 4.2.16
- Django REST Framework 3.15.2
- Django Channels 4.1.0 (WebSocket support)
- SimpleJWT 5.3.1 (JWT authentication)
- django-cors-headers 4.4.0
- Daphne 4.1.2 (ASGI server)
- SQLite (database)

**Frontend**
- React 18 + Vite
- React Router DOM
- Axios (HTTP client)
- Native WebSocket API

## Project Structure

```
chatDash/
  backend/
    manage.py
    requirements.txt
    .env.example
    config/
      settings.py           # Django settings
      urls.py               # Root URL configuration (includes GET /api/ info endpoint)
      asgi.py               # ASGI config for Channels
      wsgi.py               # WSGI config
    apps/
      accounts/             # User model, auth endpoints, online status
      chat/                 # Messages, rooms, WebSocket consumer
      common/               # Shared utilities, exception handler
    scripts/
      seed_data.py          # Demo data seeder (3 users, messages, General room)
    tests/
      test_accounts.py      # Auth API tests
      test_messages.py      # Message API tests
      test_websocket.py     # WebSocket tests
  frontend/
    src/
      api/
        auth.js             # Auth API calls + getOnlineUsers
        messages.js         # Message/room API calls
        client.js           # Axios instance with JWT interceptors
      components/
        Sidebar.jsx         # Contact list with online dots + RoomPanel
        ConversationPanel.jsx   # DM conversation view
        RoomConversationPanel.jsx  # Room conversation view
        RoomPanel.jsx       # Room list + create room form
        ProfileModal.jsx    # Profile edit modal
        MessageList.jsx     # Rendered message bubbles
        MessageComposer.jsx # Text input + send button
        StatusBanner.jsx    # WebSocket connection status
      hooks/
        useAuth.jsx         # Auth context provider + hook
        useWebSocket.js     # WebSocket connection + reconnect logic
      pages/
        ChatPage.jsx        # Main chat UI with DM + room support
        LoginPage.jsx
        RegisterPage.jsx
      styles/
        index.css           # All CSS (dark theme, layout, components)
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (SECRET_KEY, etc.)

# Run migrations
python manage.py migrate

# (Optional) Seed demo data
python scripts/seed_data.py

# (Optional) Create superuser for admin panel
python manage.py createsuperuser

# Start development server
python manage.py runserver
# OR with Daphne (recommended for WebSocket support):
daphne -p 8000 config.asgi:application
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if needed (VITE_API_URL defaults to http://localhost:8000/api)

# Start development server
npm run dev

# Build for production
npm run build
```

## Seeding Demo Data

The seed script creates 3 demo users with pre-populated messages and a General room:

```bash
cd backend
python scripts/seed_data.py
```

Demo credentials after seeding:

| Email            | Password    |
|------------------|-------------|
| alice@demo.com   | DemoPass123 |
| bob@demo.com     | DemoPass123 |
| carol@demo.com   | DemoPass123 |

## Running Tests

```bash
cd backend
python manage.py test tests --verbosity=2
```

Tests cover:
- User registration validation
- Login and JWT token issuance
- Authentication-protected endpoints
- Message history, edit, and delete with authorization
- WebSocket connection with JWT
- WebSocket message send and receive

## API Reference

### Base URL

```
http://localhost:8000/api/
```

A GET request to `/api/` returns a JSON map of all available endpoints.

### Authentication (`/api/auth/`)

| Method | Endpoint | Auth Required | Description |
|--------|----------|:---:|-------------|
| POST | `/api/auth/register` | No | Register new user |
| POST | `/api/auth/login` | No | Login and get JWT tokens |
| GET | `/api/auth/me` | Yes | Get current user profile |
| PUT/PATCH | `/api/auth/profile` | Yes | Update username / bio / avatar |
| GET | `/api/auth/users/search?q=` | Yes | Search users by username |
| GET | `/api/auth/users/online` | Yes | List currently online user IDs |
| GET | `/api/auth/users` | Yes | List all users (up to 50) |
| POST | `/api/auth/token/refresh` | No | Refresh access token |

#### Register

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "alice",
  "email": "alice@example.com",
  "password": "SecurePass123"
}
```

Response `201`:
```json
{
  "success": true,
  "message": "User registered successfully.",
  "user": { "id": 1, "username": "alice", "email": "alice@example.com", "bio": "" },
  "tokens": { "access": "<jwt>", "refresh": "<jwt>" }
}
```

#### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "SecurePass123"
}
```

Response `200`:
```json
{
  "success": true,
  "message": "Login successful.",
  "user": { "id": 1, "username": "alice", "email": "alice@example.com" },
  "tokens": { "access": "<jwt>", "refresh": "<jwt>" }
}
```

#### Online Users

```http
GET /api/auth/users/online
Authorization: Bearer <access_token>
```

Response `200`:
```json
{
  "success": true,
  "online_user_ids": [1, 3, 7]
}
```

### Messages (`/api/messages/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/messages/history/<user_id>/` | Get DM history with a user (paginated) |
| PUT/PATCH | `/api/messages/<message_id>/` | Edit a message (sender only) |
| DELETE | `/api/messages/<message_id>/delete/` | Soft-delete a message (sender only) |

#### Message History

```http
GET /api/messages/history/2/?page=1&page_size=50
Authorization: Bearer <access_token>
```

Response `200`:
```json
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "sender_id": 1,
      "receiver_id": 2,
      "room_id": null,
      "content": "Hello!",
      "is_edited": false,
      "is_deleted": false,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

### Conversations (`/api/conversations/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/conversations/` | List conversation partners |

Response `200`:
```json
{
  "success": true,
  "conversations": [
    { "id": 2, "username": "bob", "email": "bob@example.com", "last_message_at": "2024-01-01T12:00:00Z" }
  ]
}
```

### Rooms (`/api/rooms/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rooms/` | List rooms user is a member of |
| POST | `/api/rooms/` | Create a new room |
| GET | `/api/rooms/<room_id>/` | Room detail with member list |
| POST | `/api/rooms/<room_id>/members/` | Add member to room (creator only) |
| DELETE | `/api/rooms/<room_id>/members/<user_id>/` | Remove member (creator only) |
| GET | `/api/rooms/<room_id>/messages/` | Room message history (paginated) |

#### List Rooms

```http
GET /api/rooms/
Authorization: Bearer <access_token>
```

Response `200`:
```json
{
  "success": true,
  "rooms": [
    { "id": 1, "name": "General", "description": "General discussion", "member_count": 3, "created_at": "..." }
  ]
}
```

#### Create Room

```http
POST /api/rooms/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Team Chat",
  "description": "Internal team room"
}
```

Response `201`:
```json
{
  "success": true,
  "room": { "id": 2, "name": "Team Chat", "description": "Internal team room", "member_count": 1 }
}
```

#### Room Messages

```http
GET /api/rooms/1/messages/?page=1
Authorization: Bearer <access_token>
```

Response `200`:
```json
{
  "success": true,
  "messages": [
    { "id": 10, "sender_id": 1, "room_id": 1, "content": "Welcome!", "created_at": "..." }
  ]
}
```

## WebSocket Usage

Connect to: `ws://localhost:8000/ws/chat/?token=<access_token>`

The token is passed as a query parameter and validated server-side. The connection is rejected with code `4001` if the token is missing or invalid.

### Client to Server Events

```jsonc
// Send direct message
{ "type": "send_message", "receiver_id": 2, "content": "Hello!" }

// Send room message
{ "type": "send_room_message", "room_id": 1, "content": "Hello room!" }

// Edit a message (sender only)
{ "type": "edit_message", "message_id": 5, "content": "Updated content" }

// Delete a message (sender only, soft delete)
{ "type": "delete_message", "message_id": 5 }

// Typing indicator (DM)
{ "type": "typing", "receiver_id": 2, "is_typing": true }

// Typing indicator (Room)
{ "type": "typing", "room_id": 1, "is_typing": true }
```

### Server to Client Events

```jsonc
// Connection confirmed
{ "type": "connected", "success": true, "user_id": 1 }

// DM sent acknowledgement (to sender)
{ "type": "message_sent", "success": true, "message": { ... } }

// DM received (to recipient)
{ "type": "receive_message", "success": true, "message": { ... } }

// Room message sent acknowledgement (to sender)
{ "type": "room_message_sent", "success": true, "message": { ... } }

// Room message received (to room members except sender)
{ "type": "receive_room_message", "success": true, "message": { ... } }

// Message edited notification
{ "type": "message_edited", "success": true, "message": { ... } }

// Message deleted notification
{ "type": "message_deleted", "success": true, "message": { ... } }

// Typing indicator from another user
{ "type": "typing", "user_id": 2, "username": "alice", "is_typing": true }

// Error response
{ "type": "error", "success": false, "message": "Error description" }
```

### Message Object Shape

```json
{
  "id": 1,
  "sender_id": 1,
  "sender_username": "alice",
  "receiver_id": 2,
  "room_id": null,
  "content": "Hello!",
  "is_edited": false,
  "is_deleted": false,
  "edited_at": null,
  "created_at": "2024-01-01T12:00:00Z"
}
```

## Room Feature

Rooms are group conversation channels. Key characteristics:

- **Creator becomes first member** automatically on room creation.
- **Members must be added** by the room creator via `POST /api/rooms/<id>/members/`.
- **Room broadcasting** uses Django Channels InMemory layer. Members who connect after joining will receive all new messages in real time.
- **Room message history** is available via REST at `/api/rooms/<id>/messages/`.
- **Typing indicators** in rooms are scoped to the room channel and not sent back to the typing user.

## Assumptions

1. **Single-instance deployment**: Uses `InMemoryChannelLayer` instead of Redis. For production multi-instance deployment, switch to `channels_redis`.
2. **Online status**: Tracked via an in-memory dict `connected_users` in the WebSocket consumer. This is reset on server restart and does not persist across multiple server processes.
3. **Soft deletes**: Messages are soft-deleted (marked `is_deleted=True`), content replaced with `[Message deleted]`.
4. **JWT auth for WebSocket**: Token passed as query parameter `?token=<access_token>`.
5. **SQLite**: Used for development simplicity. Switch to PostgreSQL for production.
6. **Avatar**: Stored as a URL string, not an uploaded file (no media server configured).
7. **Room membership**: Only the room creator can add or remove members. Members can leave but not re-join without creator action.
8. **Pagination**: Message history endpoints support `page` and `page_size` query parameters (default page_size=50).
