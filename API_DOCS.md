# ChatDash API Documentation

Complete reference for all REST endpoints and WebSocket events.

**Base URL:** `http://localhost:8000`
**API prefix:** `/api/`
**WebSocket:** `ws://localhost:8000/ws/chat/?token=<access_token>`

---

## Table of Contents

1. [Authentication](#1-authentication)
   - [Register](#11-register)
   - [Login](#12-login)
   - [Get Current User](#13-get-current-user)
   - [Update Profile](#14-update-profile)
   - [Search Users](#15-search-users)
   - [List All Users](#16-list-all-users)
   - [Online Users](#17-online-users)
   - [Refresh Token](#18-refresh-token)
2. [Messages](#2-messages)
   - [Message History](#21-message-history)
   - [Edit Message](#22-edit-message)
   - [Delete Message](#23-delete-message)
3. [Conversations](#3-conversations)
   - [List Conversations](#31-list-conversations)
4. [Rooms](#4-rooms)
   - [List Rooms](#41-list-rooms)
   - [Create Room](#42-create-room)
   - [Room Detail](#43-room-detail)
   - [Add Member](#44-add-member)
   - [Remove Member](#45-remove-member)
   - [Room Messages](#46-room-messages)
5. [WebSocket Protocol](#5-websocket-protocol)
   - [Connection](#51-connection)
   - [Send Direct Message](#52-send-direct-message)
   - [Send Room Message](#53-send-room-message)
   - [Edit Message](#54-edit-message)
   - [Delete Message](#55-delete-message)
   - [Typing Indicator](#56-typing-indicator)
   - [Incoming Events](#57-incoming-events)
6. [Error Responses](#6-error-responses)

---

## 1. Authentication

All authenticated endpoints require the `Authorization: Bearer <access_token>` header.

### 1.1 Register

Create a new user account.

```
POST /api/auth/register
```

**Request body:**

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "SecurePass123"
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"SecurePass123"}'
```

**Response `201 Created`:**

```json
{
  "success": true,
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "bio": "",
    "avatar": null
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error `400 Bad Request`** (validation failure):

```json
{
  "success": false,
  "errors": {
    "email": ["user with this email already exists."],
    "password": ["This field is required."]
  }
}
```

---

### 1.2 Login

Authenticate with email and password.

```
POST /api/auth/login
```

**Request body:**

```json
{
  "email": "alice@example.com",
  "password": "SecurePass123"
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"SecurePass123"}'
```

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "Login successful.",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "bio": "",
    "avatar": null
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error `401 Unauthorized`:**

```json
{
  "success": false,
  "message": "Invalid credentials."
}
```

---

### 1.3 Get Current User

Fetch the authenticated user's profile.

```
GET /api/auth/me
Authorization: Bearer <access_token>
```

**curl example:**

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "bio": "Hello, I'm Alice!",
    "avatar": null
  }
}
```

---

### 1.4 Update Profile

Update the authenticated user's username, bio, or avatar URL.

```
PUT /api/auth/profile
Authorization: Bearer <access_token>
```

**Request body** (all fields optional):

```json
{
  "username": "alice_updated",
  "bio": "New bio text",
  "avatar": "https://example.com/avatar.png"
}
```

**curl example:**

```bash
curl -X PUT http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_updated","bio":"New bio text"}'
```

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "Profile updated.",
  "user": {
    "id": 1,
    "username": "alice_updated",
    "email": "alice@example.com",
    "bio": "New bio text",
    "avatar": null
  }
}
```

---

### 1.5 Search Users

Search users by username (case-insensitive, partial match).

```
GET /api/auth/users/search?q=<query>
Authorization: Bearer <access_token>
```

**curl example:**

```bash
curl "http://localhost:8000/api/auth/users/search?q=ali" \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

```json
{
  "success": true,
  "users": [
    { "id": 1, "username": "alice", "email": "alice@example.com", "bio": "" }
  ]
}
```

Returns an empty array if `q` is blank. Returns up to 10 results, excluding the requesting user.

---

### 1.6 List All Users

List all registered users (excluding the requesting user).

```
GET /api/auth/users
Authorization: Bearer <access_token>
```

**curl example:**

```bash
curl http://localhost:8000/api/auth/users \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

```json
{
  "success": true,
  "users": [
    { "id": 2, "username": "bob", "email": "bob@example.com", "bio": "" },
    { "id": 3, "username": "carol", "email": "carol@example.com", "bio": "" }
  ]
}
```

Returns up to 50 users ordered by username.

---

### 1.7 Online Users

Get the list of user IDs who currently have an active WebSocket connection.

```
GET /api/auth/users/online
Authorization: Bearer <access_token>
```

**curl example:**

```bash
curl http://localhost:8000/api/auth/users/online \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

```json
{
  "success": true,
  "online_user_ids": [1, 3]
}
```

Note: This reflects the in-memory connection state of the current server process. It resets on server restart and is not shared across multiple server instances.

---

### 1.8 Refresh Token

Obtain a new access token using a valid refresh token.

```
POST /api/auth/token/refresh
```

**Request body:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

**Response `200 OK`:**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 2. Messages

### 2.1 Message History

Retrieve paginated DM history between the authenticated user and another user.

```
GET /api/messages/history/<user_id>/?page=1&page_size=50
Authorization: Bearer <access_token>
```

**Path parameters:**
- `user_id` (integer) — ID of the other user

**Query parameters:**
- `page` (integer, default 1)
- `page_size` (integer, default 50)

**curl example:**

```bash
curl "http://localhost:8000/api/messages/history/2/?page=1&page_size=20" \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

```json
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "sender_id": 1,
      "sender_username": "alice",
      "receiver_id": 2,
      "room_id": null,
      "content": "Hello Bob!",
      "is_edited": false,
      "is_deleted": false,
      "edited_at": null,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

---

### 2.2 Edit Message

Edit the content of a message. Only the original sender can edit.

```
PUT /api/messages/<message_id>/
Authorization: Bearer <access_token>
```

**Request body:**

```json
{
  "content": "Updated message content"
}
```

**curl example:**

```bash
curl -X PUT http://localhost:8000/api/messages/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"content":"Updated message content"}'
```

**Response `200 OK`:**

```json
{
  "success": true,
  "message": {
    "id": 1,
    "content": "Updated message content",
    "is_edited": true,
    "edited_at": "2024-01-01T12:05:00Z"
  }
}
```

**Error `403 Forbidden`** (not the sender):

```json
{
  "success": false,
  "message": "You can only edit your own messages."
}
```

---

### 2.3 Delete Message

Soft-delete a message (marks as deleted, content hidden). Only the original sender can delete.

```
DELETE /api/messages/<message_id>/delete/
Authorization: Bearer <access_token>
```

**curl example:**

```bash
curl -X DELETE http://localhost:8000/api/messages/1/delete/ \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "Message deleted."
}
```

---

## 3. Conversations

### 3.1 List Conversations

Get a list of users the authenticated user has exchanged DMs with, ordered by most recent message.

```
GET /api/conversations/
Authorization: Bearer <access_token>
```

**curl example:**

```bash
curl http://localhost:8000/api/conversations/ \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

```json
{
  "success": true,
  "conversations": [
    {
      "id": 2,
      "username": "bob",
      "email": "bob@example.com",
      "bio": "",
      "last_message_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

---

## 4. Rooms

### 4.1 List Rooms

Get all rooms the authenticated user is a member of.

```
GET /api/rooms/
Authorization: Bearer <access_token>
```

**curl example:**

```bash
curl http://localhost:8000/api/rooms/ \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

```json
{
  "success": true,
  "rooms": [
    {
      "id": 1,
      "name": "General",
      "description": "General discussion room",
      "member_count": 3,
      "creator_id": 1,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

---

### 4.2 Create Room

Create a new room. The authenticated user becomes the creator and first member.

```
POST /api/rooms/
Authorization: Bearer <access_token>
```

**Request body:**

```json
{
  "name": "Team Alpha",
  "description": "Engineering team channel"
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/api/rooms/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Team Alpha","description":"Engineering team channel"}'
```

**Response `201 Created`:**

```json
{
  "success": true,
  "room": {
    "id": 2,
    "name": "Team Alpha",
    "description": "Engineering team channel",
    "member_count": 1,
    "creator_id": 1,
    "created_at": "2024-01-01T11:00:00Z"
  }
}
```

---

### 4.3 Room Detail

Get room details including the member list.

```
GET /api/rooms/<room_id>/
Authorization: Bearer <access_token>
```

**curl example:**

```bash
curl http://localhost:8000/api/rooms/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

```json
{
  "success": true,
  "room": {
    "id": 1,
    "name": "General",
    "description": "General discussion room",
    "creator_id": 1,
    "members": [
      { "id": 1, "username": "alice" },
      { "id": 2, "username": "bob" },
      { "id": 3, "username": "carol" }
    ]
  }
}
```

---

### 4.4 Add Member

Add a user to a room. Only the room creator can add members.

```
POST /api/rooms/<room_id>/members/
Authorization: Bearer <access_token>
```

**Request body:**

```json
{
  "user_id": 4
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/api/rooms/1/members/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id":4}'
```

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "User added to room."
}
```

---

### 4.5 Remove Member

Remove a member from a room. Only the room creator can remove members.

```
DELETE /api/rooms/<room_id>/members/<user_id>/
Authorization: Bearer <access_token>
```

**curl example:**

```bash
curl -X DELETE http://localhost:8000/api/rooms/1/members/4/ \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "User removed from room."
}
```

---

### 4.6 Room Messages

Get paginated message history for a room. User must be a room member.

```
GET /api/rooms/<room_id>/messages/?page=1
Authorization: Bearer <access_token>
```

**curl example:**

```bash
curl "http://localhost:8000/api/rooms/1/messages/?page=1" \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

```json
{
  "success": true,
  "messages": [
    {
      "id": 10,
      "sender_id": 1,
      "sender_username": "alice",
      "receiver_id": null,
      "room_id": 1,
      "content": "Welcome everyone!",
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

---

## 5. WebSocket Protocol

### 5.1 Connection

Connect with a valid JWT access token as a query parameter:

```
ws://localhost:8000/ws/chat/?token=<access_token>
```

On successful connection the server sends:

```json
{
  "type": "connected",
  "success": true,
  "message": "Connected to chat server.",
  "user_id": 1
}
```

If the token is missing or invalid the connection is closed with code `4001`.

**JavaScript example:**

```javascript
const token = localStorage.getItem('access_token');
const ws = new WebSocket(`ws://localhost:8000/ws/chat/?token=${token}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

ws.onopen = () => console.log('Connected');
ws.onclose = (e) => console.log('Disconnected', e.code);
```

---

### 5.2 Send Direct Message

```json
{
  "type": "send_message",
  "receiver_id": 2,
  "content": "Hello Bob!"
}
```

**Fields:**
- `receiver_id` (integer, required) — recipient user ID
- `content` (string, required, 1-5000 chars) — message body

**ACK to sender:**

```json
{
  "type": "message_sent",
  "success": true,
  "message": { "id": 1, "sender_id": 1, "receiver_id": 2, "content": "Hello Bob!", ... }
}
```

**Delivered to recipient (if online):**

```json
{
  "type": "receive_message",
  "success": true,
  "message": { ... }
}
```

---

### 5.3 Send Room Message

```json
{
  "type": "send_room_message",
  "room_id": 1,
  "content": "Hello everyone!"
}
```

**Fields:**
- `room_id` (integer, required) — target room ID
- `content` (string, required, 1-5000 chars) — message body

The sender must be a room member. Returns an error otherwise.

**ACK to sender:**

```json
{
  "type": "room_message_sent",
  "success": true,
  "message": { "id": 10, "sender_id": 1, "room_id": 1, "content": "Hello everyone!", ... }
}
```

**Broadcast to room members (excluding sender):**

```json
{
  "type": "receive_room_message",
  "success": true,
  "message": { ... }
}
```

---

### 5.4 Edit Message

```json
{
  "type": "edit_message",
  "message_id": 5,
  "content": "Updated content"
}
```

**Fields:**
- `message_id` (integer, required)
- `content` (string, required)

Sender-only. Cannot edit deleted messages.

**Response (to both parties):**

```json
{
  "type": "message_edited",
  "success": true,
  "message": { "id": 5, "content": "Updated content", "is_edited": true, "edited_at": "..." }
}
```

---

### 5.5 Delete Message

```json
{
  "type": "delete_message",
  "message_id": 5
}
```

**Fields:**
- `message_id` (integer, required)

Sender-only. Soft delete — message object remains but `is_deleted` is set to `true`.

**Response (to both parties):**

```json
{
  "type": "message_deleted",
  "success": true,
  "message": { "id": 5, "is_deleted": true, "content": "[Message deleted]", ... }
}
```

---

### 5.6 Typing Indicator

**DM typing:**

```json
{
  "type": "typing",
  "receiver_id": 2,
  "is_typing": true
}
```

**Room typing:**

```json
{
  "type": "typing",
  "room_id": 1,
  "is_typing": true
}
```

Set `is_typing: false` to cancel. Sent to the recipient/room members (not back to sender).

**Received by other user:**

```json
{
  "type": "typing",
  "user_id": 1,
  "username": "alice",
  "is_typing": true
}
```

---

### 5.7 Incoming Events

Summary of all event types the client may receive:

| `type` | Trigger | Description |
|--------|---------|-------------|
| `connected` | On connect | Connection confirmed with user_id |
| `message_sent` | After send_message | DM saved, returned to sender |
| `receive_message` | send_message | DM delivered to recipient |
| `room_message_sent` | After send_room_message | Room msg saved, returned to sender |
| `receive_room_message` | send_room_message | Room msg delivered to other members |
| `message_edited` | After edit_message | Edited message to both parties |
| `message_deleted` | After delete_message | Soft-deleted message to both parties |
| `typing` | typing event | Typing status from another user |
| `error` | Any invalid input | Error description |

---

## 6. Error Responses

All error responses follow this shape:

```json
{
  "success": false,
  "message": "Human-readable error description."
}
```

Or for validation errors:

```json
{
  "success": false,
  "errors": {
    "field_name": ["Error detail."]
  }
}
```

**Common HTTP status codes:**

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (not allowed) |
| 404 | Not Found |
| 500 | Internal Server Error |

**WebSocket close codes:**

| Code | Meaning |
|------|---------|
| 4001 | Authentication failed (invalid/missing token) |
