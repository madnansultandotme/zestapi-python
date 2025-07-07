# WebSocket Chat Application

A real-time chat application built with ZestAPI demonstrating WebSocket functionality.

## Features

- **Real-time messaging**: Instant message delivery using WebSockets
- **Multiple chat rooms**: Join different chat rooms
- **User management**: Set username and track online users
- **Message history**: View recent messages when joining a room
- **Typing indicators**: See when other users are typing
- **User list**: See who's currently online in each room
- **Modern UI**: Clean, responsive chat interface

## WebSocket Events

### Client to Server
- `join_room` - Join a chat room
- `leave_room` - Leave a chat room
- `send_message` - Send a message to the current room
- `typing_start` - Indicate user is typing
- `typing_stop` - Indicate user stopped typing

### Server to Client
- `user_joined` - User joined the room
- `user_left` - User left the room
- `new_message` - New message received
- `user_typing` - Someone is typing
- `user_stopped_typing` - Someone stopped typing
- `room_users` - List of users in current room
- `error` - Error message

## Message Format

```json
{
  "type": "event_type",
  "data": {
    "room": "room_name",
    "username": "user_name",
    "message": "message_content",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## Installation

```bash
cd examples/websocket-chat
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

The chat application will be available at `http://localhost:8000`

## Usage

1. Open `http://localhost:8000` in your browser
2. Enter your username
3. Select or create a chat room
4. Start chatting in real-time!

## Technical Details

### WebSocket Connection
- Endpoint: `ws://localhost:8000/ws`
- Protocol: JSON-based message exchange
- Automatic reconnection on connection loss

### Room Management
- Dynamic room creation
- Persistent message history (in-memory)
- User presence tracking
- Room-based message broadcasting

### Message Types
- **Text messages**: Regular chat messages
- **System messages**: Join/leave notifications
- **Typing indicators**: Real-time typing status
- **User lists**: Online user updates

## Production Considerations

For production deployment:
- Use Redis for message persistence and pub/sub
- Implement user authentication
- Add message encryption
- Implement rate limiting
- Add message moderation
- Use horizontal scaling with sticky sessions
- Add monitoring and logging
- Implement proper error handling
- Add file/image sharing capabilities
