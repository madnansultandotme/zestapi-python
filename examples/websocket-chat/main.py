import json
from datetime import datetime

from chat_manager import ChatManager

from zestapi import HTMLResponse, ORJSONResponse, ZestAPI, websocket_route

# Create ZestAPI instance
app_instance = ZestAPI()

# Global chat manager
chat_manager = ChatManager()


# Serve the chat interface
async def chat_interface(request):
    """Serve the chat HTML interface"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZestAPI Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 800px;
            height: 80vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .login-screen {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            padding: 40px;
        }
        
        .chat-header {
            background: #667eea;
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-body {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        
        .sidebar {
            width: 250px;
            background: #f8f9fa;
            border-right: 1px solid #e9ecef;
            padding: 20px;
            overflow-y: auto;
        }
        
        .messages-container {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 70%;
            word-wrap: break-word;
        }
        
        .message.own {
            background: #667eea;
            color: white;
            margin-left: auto;
        }
        
        .message.other {
            background: white;
            border: 1px solid #e9ecef;
        }
        
        .message.system {
            background: #e7f3ff;
            border: 1px solid #b3d9ff;
            text-align: center;
            font-style: italic;
            max-width: 100%;
            margin: 10px auto;
        }
        
        .message-input {
            display: flex;
            padding: 20px;
            background: white;
            border-top: 1px solid #e9ecef;
        }
        
        .message-input input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            margin-right: 10px;
            outline: none;
        }
        
        .message-input input:focus {
            border-color: #667eea;
        }
        
        .message-input button {
            padding: 12px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
        }
        
        .message-input button:hover {
            background: #5a6fd8;
        }
        
        .input-group {
            margin-bottom: 20px;
            width: 100%;
            max-width: 300px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        .input-group input, .input-group select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            outline: none;
        }
        
        .input-group input:focus, .input-group select:focus {
            border-color: #667eea;
        }
        
        .btn {
            padding: 12px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 16px;
        }
        
        .btn:hover {
            background: #5a6fd8;
        }
        
        .users-list {
            margin-top: 20px;
        }
        
        .users-list h3 {
            margin-bottom: 10px;
            color: #495057;
        }
        
        .user-item {
            padding: 8px 12px;
            background: white;
            border-radius: 8px;
            margin-bottom: 5px;
            border: 1px solid #e9ecef;
        }
        
        .typing-indicator {
            padding: 10px 20px;
            font-style: italic;
            color: #6c757d;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }
        
        .connection-status {
            font-size: 12px;
            opacity: 0.8;
        }
        
        .hidden {
            display: none !important;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <!-- Login Screen -->
        <div id="loginScreen" class="login-screen">
            <h1 style="margin-bottom: 30px; color: #667eea;">ZestAPI Chat</h1>
            <div class="input-group">
                <label for="username">Username</label>
                <input type="text" id="username" placeholder="Enter your username">
            </div>
            <div class="input-group">
                <label for="roomName">Room</label>
                <input type="text" id="roomName" placeholder="Enter room name" value="general">
            </div>
            <button class="btn" onclick="joinChat()">Join Chat</button>
        </div>
        
        <!-- Chat Interface -->
        <div id="chatInterface" class="hidden">
            <div class="chat-header">
                <div>
                    <h2 id="currentRoom">Room: general</h2>
                    <div class="connection-status" id="connectionStatus">Connected</div>
                </div>
                <button class="btn" onclick="leaveChat()" style="background: #dc3545;">Leave</button>
            </div>
            
            <div class="chat-body">
                <div class="sidebar">
                    <div class="users-list">
                        <h3>Online Users</h3>
                        <div id="usersList"></div>
                    </div>
                </div>
                
                <div class="messages-container">
                    <div class="messages" id="messages"></div>
                    <div class="typing-indicator hidden" id="typingIndicator"></div>
                    <div class="message-input">
                        <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
                        <button onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let socket = null;
        let currentUser = null;
        let currentRoom = null;
        let typingTimer = null;
        
        function joinChat() {
            const username = document.getElementById('username').value.trim();
            const roomName = document.getElementById('roomName').value.trim();
            
            if (!username || !roomName) {
                alert('Please enter both username and room name');
                return;
            }
            
            currentUser = username;
            currentRoom = roomName;
            
            // Connect to WebSocket
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            socket = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            socket.onopen = function() {
                console.log('Connected to WebSocket');
                document.getElementById('connectionStatus').textContent = 'Connected';
                
                // Join room
                socket.send(JSON.stringify({
                    type: 'join_room',
                    data: {
                        username: currentUser,
                        room: currentRoom
                    }
                }));
                
                // Show chat interface
                document.getElementById('loginScreen').classList.add('hidden');
                document.getElementById('chatInterface').classList.remove('hidden');
                document.getElementById('currentRoom').textContent = `Room: ${currentRoom}`;
                document.getElementById('messageInput').focus();
            };
            
            socket.onmessage = function(event) {
                const message = JSON.parse(event.data);
                handleMessage(message);
            };
            
            socket.onclose = function() {
                console.log('WebSocket connection closed');
                document.getElementById('connectionStatus').textContent = 'Disconnected';
            };
            
            socket.onerror = function(error) {
                console.error('WebSocket error:', error);
                alert('Connection failed. Please try again.');
            };
        }
        
        function leaveChat() {
            if (socket) {
                socket.send(JSON.stringify({
                    type: 'leave_room',
                    data: {
                        username: currentUser
                    }
                }));
                socket.close();
            }
            
            // Reset UI
            document.getElementById('chatInterface').classList.add('hidden');
            document.getElementById('loginScreen').classList.remove('hidden');
            document.getElementById('messages').innerHTML = '';
            document.getElementById('usersList').innerHTML = '';
            currentUser = null;
            currentRoom = null;
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message || !socket) return;
            
            socket.send(JSON.stringify({
                type: 'send_message',
                data: {
                    username: currentUser,
                    room: currentRoom,
                    message: message
                }
            }));
            
            input.value = '';
            stopTyping();
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            } else {
                startTyping();
            }
        }
        
        function startTyping() {
            if (!socket) return;
            
            socket.send(JSON.stringify({
                type: 'typing_start',
                data: {
                    username: currentUser,
                    room: currentRoom
                }
            }));
            
            // Clear existing timer
            if (typingTimer) {
                clearTimeout(typingTimer);
            }
            
            // Stop typing after 3 seconds of inactivity
            typingTimer = setTimeout(stopTyping, 3000);
        }
        
        function stopTyping() {
            if (!socket) return;
            
            socket.send(JSON.stringify({
                type: 'typing_stop',
                data: {
                    username: currentUser,
                    room: currentRoom
                }
            }));
            
            if (typingTimer) {
                clearTimeout(typingTimer);
                typingTimer = null;
            }
        }
        
        function handleMessage(message) {
            switch (message.type) {
                case 'new_message':
                case 'user_joined':
                case 'user_left':
                    addMessage(message.data);
                    break;
                case 'room_users':
                    updateUsersList(message.data.users);
                    break;
                case 'user_typing':
                    showTypingIndicator(message.data.users);
                    break;
                case 'message_history':
                    message.data.messages.forEach(msg => addMessage(msg));
                    break;
                case 'error':
                    alert('Error: ' + message.data.message);
                    break;
            }
        }
        
        function addMessage(messageData) {
            const messagesContainer = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            
            if (messageData.type === 'system') {
                messageDiv.className += ' system';
                messageDiv.innerHTML = messageData.message;
            } else {
                if (messageData.username === currentUser) {
                    messageDiv.className += ' own';
                } else {
                    messageDiv.className += ' other';
                }
                
                const time = new Date(messageData.timestamp).toLocaleTimeString();
                messageDiv.innerHTML = `
                    <div style="font-weight: bold; margin-bottom: 5px;">${messageData.username}</div>
                    <div>${messageData.message}</div>
                    <div style="font-size: 12px; opacity: 0.7; margin-top: 5px;">${time}</div>
                `;
            }
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function updateUsersList(users) {
            const usersList = document.getElementById('usersList');
            usersList.innerHTML = '';
            
            users.forEach(username => {
                const userDiv = document.createElement('div');
                userDiv.className = 'user-item';
                userDiv.textContent = username;
                if (username === currentUser) {
                    userDiv.style.fontWeight = 'bold';
                    userDiv.style.background = '#e7f3ff';
                }
                usersList.appendChild(userDiv);
            });
        }
        
        function showTypingIndicator(typingUsers) {
            const indicator = document.getElementById('typingIndicator');
            const filteredUsers = typingUsers.filter(user => user !== currentUser);
            
            if (filteredUsers.length === 0) {
                indicator.classList.add('hidden');
            } else {
                indicator.classList.remove('hidden');
                if (filteredUsers.length === 1) {
                    indicator.textContent = `${filteredUsers[0]} is typing...`;
                } else {
                    indicator.textContent = `${filteredUsers.join(', ')} are typing...`;
                }
            }
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(html_content)


@websocket_route("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for chat functionality"""
    await websocket.accept()

    username = None
    current_room = None

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            message_type = message.get("type")
            message_data = message.get("data", {})

            if message_type == "join_room":
                username = message_data.get("username")
                room_name = message_data.get("room")

                if username and room_name:
                    room, join_message = chat_manager.join_room(
                        username, room_name, websocket
                    )
                    current_room = room

                    # Send recent messages to new user
                    recent_messages = room.get_recent_messages()
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "message_history",
                                "data": {"messages": recent_messages},
                            }
                        )
                    )

                    # Broadcast join message to others
                    await room.broadcast(
                        {"type": "user_joined", "data": join_message}, username
                    )

                    # Send updated user list to all
                    user_list_message = {
                        "type": "room_users",
                        "data": {"users": room.get_user_list()},
                    }
                    await room.broadcast(user_list_message)

            elif message_type == "leave_room":
                if username and current_room:
                    room, leave_message = chat_manager.leave_current_room(username)
                    if room and leave_message:
                        # Broadcast leave message
                        await room.broadcast(
                            {"type": "user_left", "data": leave_message}
                        )

                        # Send updated user list
                        user_list_message = {
                            "type": "room_users",
                            "data": {"users": room.get_user_list()},
                        }
                        await room.broadcast(user_list_message)

                    current_room = None

            elif message_type == "send_message":
                if username and current_room:
                    message_content = message_data.get("message", "").strip()
                    if message_content:
                        chat_message = {
                            "type": "message",
                            "username": username,
                            "message": message_content,
                            "timestamp": datetime.utcnow().isoformat(),
                            "room": current_room.name,
                        }

                        # Add to room history
                        current_room.add_message(chat_message)

                        # Broadcast to all users in room
                        await current_room.broadcast(
                            {"type": "new_message", "data": chat_message}
                        )

            elif message_type == "typing_start":
                if username and current_room:
                    typing_users = current_room.set_typing(username, True)
                    await current_room.broadcast(
                        {"type": "user_typing", "data": {"users": typing_users}}
                    )

            elif message_type == "typing_stop":
                if username and current_room:
                    typing_users = current_room.set_typing(username, False)
                    await current_room.broadcast(
                        {"type": "user_typing", "data": {"users": typing_users}}
                    )

    except Exception as e:
        print(f"WebSocket error: {e}")

    finally:
        # Clean up on disconnect
        if username and current_room:
            room, leave_message = chat_manager.leave_current_room(username)
            if room and leave_message:
                try:
                    await room.broadcast({"type": "user_left", "data": leave_message})
                    user_list_message = {
                        "type": "room_users",
                        "data": {"users": room.get_user_list()},
                    }
                    await room.broadcast(user_list_message)
                except:
                    pass


# API endpoints
async def root(request):
    return ORJSONResponse(
        {
            "message": "Welcome to ZestAPI WebSocket Chat",
            "version": "1.0.0",
            "endpoints": {"chat": "GET /", "websocket": "ws://localhost:8000/ws"},
            "features": [
                "Real-time messaging",
                "Multiple chat rooms",
                "User presence tracking",
                "Typing indicators",
                "Message history",
            ],
        }
    )


async def get_rooms(request):
    """Get list of active chat rooms"""
    rooms = chat_manager.get_room_list()
    return ORJSONResponse({"rooms": rooms, "total": len(rooms)})


async def health_check(request):
    return ORJSONResponse(
        {
            "status": "healthy",
            "service": "zestapi-websocket-chat",
            "active_rooms": len(chat_manager.rooms),
            "total_users": sum(len(room.users) for room in chat_manager.rooms.values()),
        }
    )


# Add routes
app_instance.add_route("/", chat_interface)
app_instance.add_route("/api", root)
app_instance.add_route("/api/rooms", get_rooms)
app_instance.add_route("/health", health_check)

if __name__ == "__main__":
    print("[*] Starting ZestAPI WebSocket Chat...")
    print("[*] Open http://localhost:8000 in your browser to start chatting!")
    print("[*] WebSocket endpoint: ws://localhost:8000/ws")
    app_instance.run()
