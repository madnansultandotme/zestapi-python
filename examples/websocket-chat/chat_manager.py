from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import json

class ChatRoom:
    def __init__(self, name: str):
        self.name = name
        self.users: Dict[str, Any] = {}  # username -> websocket
        self.messages: List[Dict] = []
        self.typing_users: Set[str] = set()
        self.max_messages = 100  # Keep last 100 messages
    
    def add_user(self, username: str, websocket):
        """Add user to room"""
        self.users[username] = websocket
        
        # Add join message
        message = {
            "type": "system",
            "username": "System",
            "message": f"{username} joined the room",
            "timestamp": datetime.utcnow().isoformat(),
            "room": self.name
        }
        self.add_message(message)
        
        return message
    
    def remove_user(self, username: str):
        """Remove user from room"""
        if username in self.users:
            del self.users[username]
            self.typing_users.discard(username)
            
            # Add leave message
            message = {
                "type": "system",
                "username": "System",
                "message": f"{username} left the room",
                "timestamp": datetime.utcnow().isoformat(),
                "room": self.name
            }
            self.add_message(message)
            
            return message
        return None
    
    def add_message(self, message: Dict):
        """Add message to room history"""
        self.messages.append(message)
        
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_recent_messages(self, count: int = 20) -> List[Dict]:
        """Get recent messages"""
        return self.messages[-count:]
    
    def get_user_list(self) -> List[str]:
        """Get list of usernames in room"""
        return list(self.users.keys())
    
    async def broadcast(self, message: Dict, exclude_user: Optional[str] = None):
        """Broadcast message to all users in room"""
        message_json = json.dumps(message)
        
        # Remove disconnected users
        disconnected_users = []
        
        for username, websocket in self.users.items():
            if exclude_user and username == exclude_user:
                continue
                
            try:
                await websocket.send_text(message_json)
            except Exception:
                # Mark for removal if sending fails
                disconnected_users.append(username)
        
        # Remove disconnected users
        for username in disconnected_users:
            self.remove_user(username)
    
    def set_typing(self, username: str, typing: bool):
        """Set typing status for user"""
        if typing:
            self.typing_users.add(username)
        else:
            self.typing_users.discard(username)
        
        return list(self.typing_users)

class ChatManager:
    def __init__(self):
        self.rooms: Dict[str, ChatRoom] = {}
        self.user_rooms: Dict[str, str] = {}  # username -> current room
    
    def get_or_create_room(self, room_name: str) -> ChatRoom:
        """Get existing room or create new one"""
        if room_name not in self.rooms:
            self.rooms[room_name] = ChatRoom(room_name)
        return self.rooms[room_name]
    
    def join_room(self, username: str, room_name: str, websocket):
        """Join user to room"""
        # Leave current room if any
        self.leave_current_room(username)
        
        # Join new room
        room = self.get_or_create_room(room_name)
        join_message = room.add_user(username, websocket)
        self.user_rooms[username] = room_name
        
        return room, join_message
    
    def leave_current_room(self, username: str):
        """Leave user's current room"""
        if username in self.user_rooms:
            room_name = self.user_rooms[username]
            room = self.rooms.get(room_name)
            
            if room:
                leave_message = room.remove_user(username)
                
                # Remove empty rooms
                if not room.users:
                    del self.rooms[room_name]
                
                return room, leave_message
            
            del self.user_rooms[username]
        
        return None, None
    
    def get_user_room(self, username: str) -> Optional[ChatRoom]:
        """Get user's current room"""
        room_name = self.user_rooms.get(username)
        if room_name:
            return self.rooms.get(room_name)
        return None
    
    def get_room_list(self) -> List[Dict]:
        """Get list of all rooms with user counts"""
        return [
            {
                "name": room_name,
                "user_count": len(room.users),
                "users": room.get_user_list()
            }
            for room_name, room in self.rooms.items()
        ]
