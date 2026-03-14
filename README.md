# ChatDash - Real-Time Chat Application

A full-stack real-time chat application built with Django + Channels (backend) and React + Vite (frontend).

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
      settings.py       # Django settings
      urls.py           # Root URL configuration
      asgi.py           # ASGI config for Channels
      wsgi.py           # WSGI config
    apps/
      accounts/         # User model, auth endpoints
      chat/             # Messages, rooms, WebSocket consumer
      common/           # Shared utilities, exception handler
    tests/
      test_accounts.py  # Auth API tests
      test_messages.py  # Message API tests
      test_websocket.py # WebSocket tests
  frontend/
    src/
      api/              # Axios API clients
      components/       # React UI components
      hooks/            # Custom React hooks
      pages/            # Page components
      styles/           # CSS styles
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
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser (optional)
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
# Edit .env if needed

# Start development server
npm run dev

# Build for production
npm run build
```

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

## API Summary

### Authentication (`/api/auth/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | Login and get JWT tokens |
| GET | `/me` | Get current user |
| PUT/PATCH | `/profile` | Update user profile |
| GET | `/users/search?q=` | Search users by username |
| GET | `/users` | List all users |
| POST | `/token/refresh` | Refresh access token |

### Messages (`/api/messages/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/history/<user_id>/` | Get message history with user |
| PUT/PATCH | `/<message_id>/` | Edit a message |
| DELETE | `/<message_id>/delete/` | Soft-delete a message |

### Conversations (`/api/conversations/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List conversation partners |

### Rooms (`/api/rooms/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/` | List rooms or create room |
| GET | `/<room_id>/` | Room detail with members |
| POST | `/<room_id>/members/` | Add member to room |
| DELETE | `/<room_id>/members/<user_id>/` | Remove member |
| GET | `/<room_id>/messages/` | Room message history |

## WebSocket Usage

Connect to: `ws://localhost:8000/ws/chat/?token=<access_token>`

### Client -> Server Events

```json
// Send direct message
{ "type": "send_message", "receiver_id": 2, "content": "Hello!" }

// Send room message
{ "type": "send_room_message", "room_id": 1, "content": "Hello room!" }

// Edit message
{ "type": "edit_message", "message_id": 5, "content": "Updated content" }

// Delete message
{ "type": "delete_message", "message_id": 5 }

// Typing indicator
{ "type": "typing", "receiver_id": 2, "is_typing": true }
```

### Server -> Client Events

```json
// Connection confirmed
{ "type": "connected", "success": true, "user_id": 1 }

// Message sent acknowledgement
{ "type": "message_sent", "success": true, "message": {...} }

// Receiving a message
{ "type": "receive_message", "success": true, "message": {...} }

// Message edited
{ "type": "message_edited", "success": true, "message": {...} }

// Message deleted
{ "type": "message_deleted", "success": true, "message": {...} }

// Typing indicator from other user
{ "type": "typing", "user_id": 2, "username": "alice", "is_typing": true }

// Error
{ "type": "error", "success": false, "message": "Error description" }
```

## Assumptions

1. **Single-instance deployment**: Uses `InMemoryChannelLayer` instead of Redis. For production multi-instance deployment, switch to `channels_redis`.
2. **Soft deletes**: Messages are soft-deleted (marked `is_deleted=True`), content replaced with `[Message deleted]`.
3. **JWT auth for WebSocket**: Token passed as query parameter `?token=<access_token>`.
4. **SQLite**: Used for development simplicity. Switch to PostgreSQL for production.
5. **Avatar**: Stored as a URL string, not an uploaded file (no media server configured).
6. **Room broadcasting**: Uses Django Channels InMemory layer; room members must connect after joining to receive room messages.
