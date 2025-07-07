import json

from stream_manager import StreamManager

from zestapi import HTMLResponse, ORJSONResponse, ZestAPI, websocket_route

# Create ZestAPI instance
app_instance = ZestAPI()

# Global stream manager
stream_manager = StreamManager()


# Serve the video streaming interface
async def video_interface(request):
    """Serve the video streaming HTML interface"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZestAPI Video Streaming</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: #667eea;
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .content {
            padding: 30px;
        }
        
        .controls {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .control-group label {
            font-weight: 600;
            color: #495057;
        }
        
        .control-group select, .control-group input {
            padding: 10px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            outline: none;
        }
        
        .control-group select:focus, .control-group input:focus {
            border-color: #667eea;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .video-container {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }
        
        .video-player {
            background: #000;
            border-radius: 15px;
            overflow: hidden;
            position: relative;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .video-player canvas {
            max-width: 100%;
            max-height: 100%;
        }
        
        .no-video {
            color: white;
            font-size: 18px;
            text-align: center;
        }
        
        .stream-info {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
        }
        
        .stream-info h3 {
            margin-bottom: 15px;
            color: #495057;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .info-item:last-child {
            border-bottom: none;
        }
        
        .info-label {
            font-weight: 600;
            color: #6c757d;
        }
        
        .info-value {
            color: #495057;
        }
        
        .streams-list {
            margin-top: 20px;
        }
        
        .stream-item {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .stream-item:hover {
            border-color: #667eea;
            background: #f8f9fa;
        }
        
        .stream-item.active {
            border-color: #667eea;
            background: #e7f3ff;
        }
        
        .stream-title {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .stream-meta {
            font-size: 12px;
            color: #6c757d;
        }
        
        .status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .status.connected {
            background: #d4edda;
            color: #155724;
        }
        
        .status.disconnected {
            background: #f8d7da;
            color: #721c24;
        }
        
        .status.streaming {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        @media (max-width: 768px) {
            .video-container {
                grid-template-columns: 1fr;
            }
            
            .controls {
                flex-direction: column;
                align-items: stretch;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ZestAPI Video Streaming</h1>
            <p>Real-time video streaming with WebSockets</p>
        </div>
        
        <div class="content">
            <div class="controls">
                <div class="control-group">
                    <label for="quality">Quality</label>
                    <select id="quality">
                        <option value="low">Low (320p)</option>
                        <option value="medium" selected>Medium (480p)</option>
                        <option value="high">High (720p)</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label for="camera">Camera</label>
                    <select id="camera">
                        <option value="0">Camera 0 (Default)</option>
                        <option value="1">Camera 1</option>
                        <option value="2">Camera 2</option>
                    </select>
                </div>
                
                <button id="startStreamBtn" class="btn btn-success">Start Stream</button>
                <button id="stopStreamBtn" class="btn btn-danger" disabled>Stop Stream</button>
                <button id="refreshStreamsBtn" class="btn btn-primary">Refresh Streams</button>
            </div>
            
            <div class="video-container">
                <div class="video-player">
                    <canvas id="videoCanvas" style="display: none;"></canvas>
                    <div id="noVideo" class="no-video">
                        No video stream active. Start a stream or select an existing one.
                    </div>
                </div>
                
                <div class="stream-info">
                    <h3>Stream Information</h3>
                    <div id="streamInfo">
                        <div class="info-item">
                            <span class="info-label">Status:</span>
                            <span class="info-value">
                                <span id="connectionStatus" class="status disconnected">Disconnected</span>
                            </span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Stream ID:</span>
                            <span class="info-value" id="streamId">None</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Quality:</span>
                            <span class="info-value" id="streamQuality">None</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Viewers:</span>
                            <span class="info-value" id="viewerCount">0</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Frames:</span>
                            <span class="info-value" id="frameCount">0</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">FPS:</span>
                            <span class="info-value" id="currentFps">0</span>
                        </div>
                    </div>
                    
                    <div class="streams-list">
                        <h3>Available Streams</h3>
                        <div id="streamsList">
                            <p style="color: #6c757d; text-align: center; padding: 20px;">
                                No active streams
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let socket = null;
        let currentStreamId = null;
        let isStreaming = false;
        let frameCount = 0;
        let lastFrameTime = 0;
        let fpsCounter = 0;
        
        const canvas = document.getElementById('videoCanvas');
        const ctx = canvas.getContext('2d');
        const noVideoDiv = document.getElementById('noVideo');
        
        // UI Elements
        const startStreamBtn = document.getElementById('startStreamBtn');
        const stopStreamBtn = document.getElementById('stopStreamBtn');
        const refreshStreamsBtn = document.getElementById('refreshStreamsBtn');
        const qualitySelect = document.getElementById('quality');
        const cameraSelect = document.getElementById('camera');
        
        // Info elements
        const connectionStatus = document.getElementById('connectionStatus');
        const streamId = document.getElementById('streamId');
        const streamQuality = document.getElementById('streamQuality');
        const viewerCount = document.getElementById('viewerCount');
        const frameCountEl = document.getElementById('frameCount');
        const currentFps = document.getElementById('currentFps');
        const streamsList = document.getElementById('streamsList');
        
        // Event listeners
        startStreamBtn.addEventListener('click', startStream);
        stopStreamBtn.addEventListener('click', stopStream);
        refreshStreamsBtn.addEventListener('click', loadStreams);
        
        // Load streams on page load
        window.addEventListener('load', loadStreams);
        
        async function startStream() {
            try {
                const quality = qualitySelect.value;
                const camera = parseInt(cameraSelect.value);
                
                const response = await fetch('/api/streams', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        quality: quality,
                        camera_index: camera
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    currentStreamId = data.stream_id;
                    
                    // Connect to WebSocket
                    connectToStream(currentStreamId);
                    
                    // Update UI
                    startStreamBtn.disabled = true;
                    stopStreamBtn.disabled = false;
                    isStreaming = true;
                    
                    updateStreamInfo({
                        stream_id: currentStreamId,
                        quality: quality,
                        is_active: true
                    });
                    
                } else {
                    alert('Failed to start stream');
                }
            } catch (error) {
                console.error('Error starting stream:', error);
                alert('Error starting stream');
            }
        }
        
        async function stopStream() {
            if (currentStreamId) {
                try {
                    await fetch(`/api/streams/${currentStreamId}`, {
                        method: 'DELETE'
                    });
                } catch (error) {
                    console.error('Error stopping stream:', error);
                }
            }
            
            if (socket) {
                socket.close();
                socket = null;
            }
            
            // Reset UI
            startStreamBtn.disabled = false;
            stopStreamBtn.disabled = true;
            isStreaming = false;
            currentStreamId = null;
            frameCount = 0;
            
            hideVideo();
            updateConnectionStatus('disconnected');
            resetStreamInfo();
            loadStreams();
        }
        
        function connectToStream(streamId) {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            socket = new WebSocket(`${protocol}//${window.location.host}/ws/viewer/${streamId}`);
            
            socket.onopen = function() {
                console.log('Connected to stream:', streamId);
                updateConnectionStatus('connected');
            };
            
            socket.onmessage = function(event) {
                const message = JSON.parse(event.data);
                handleStreamMessage(message);
            };
            
            socket.onclose = function() {
                console.log('Stream connection closed');
                updateConnectionStatus('disconnected');
                if (isStreaming) {
                    // Try to reconnect after a delay
                    setTimeout(() => {
                        if (currentStreamId) {
                            connectToStream(currentStreamId);
                        }
                    }, 2000);
                }
            };
            
            socket.onerror = function(error) {
                console.error('Stream error:', error);
                updateConnectionStatus('disconnected');
            };
        }
        
        function handleStreamMessage(message) {
            if (message.type === 'frame') {
                displayFrame(message.data);
                updateFrameStats();
            } else if (message.type === 'stream_info') {
                updateStreamInfo(message.data);
            }
        }
        
        function displayFrame(frameData) {
            const img = new Image();
            img.onload = function() {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                
                // Show canvas, hide no video message
                canvas.style.display = 'block';
                noVideoDiv.style.display = 'none';
            };
            img.src = 'data:image/jpeg;base64,' + frameData.frame;
            
            frameCount++;
            frameCountEl.textContent = frameCount;
        }
        
        function updateFrameStats() {
            const now = Date.now();
            if (lastFrameTime > 0) {
                const timeDiff = now - lastFrameTime;
                fpsCounter++;
                
                // Calculate FPS every second
                if (fpsCounter >= 30) {
                    const fps = Math.round(1000 / (timeDiff));
                    currentFps.textContent = fps;
                    fpsCounter = 0;
                }
            }
            lastFrameTime = now;
        }
        
        function hideVideo() {
            canvas.style.display = 'none';
            noVideoDiv.style.display = 'block';
        }
        
        function updateConnectionStatus(status) {
            connectionStatus.textContent = status.charAt(0).toUpperCase() + status.slice(1);
            connectionStatus.className = `status ${status}`;
        }
        
        function updateStreamInfo(info) {
            streamId.textContent = info.stream_id || 'None';
            streamQuality.textContent = info.quality || 'None';
            viewerCount.textContent = info.viewer_count || '0';
        }
        
        function resetStreamInfo() {
            streamId.textContent = 'None';
            streamQuality.textContent = 'None';
            viewerCount.textContent = '0';
            frameCountEl.textContent = '0';
            currentFps.textContent = '0';
        }
        
        async function loadStreams() {
            try {
                const response = await fetch('/api/streams');
                const data = await response.json();
                
                displayStreamsList(data.streams);
            } catch (error) {
                console.error('Error loading streams:', error);
            }
        }
        
        function displayStreamsList(streams) {
            if (streams.length === 0) {
                streamsList.innerHTML = `
                    <p style="color: #6c757d; text-align: center; padding: 20px;">
                        No active streams
                    </p>
                `;
                return;
            }
            
            streamsList.innerHTML = streams.map(stream => `
                <div class="stream-item ${stream.stream_id === currentStreamId ? 'active' : ''}"
                     onclick="joinStream('${stream.stream_id}')">
                    <div class="stream-title">${stream.stream_id}</div>
                    <div class="stream-meta">
                        Quality: ${stream.quality} | 
                        Viewers: ${stream.viewer_count} | 
                        Frames: ${stream.frame_count}
                    </div>
                </div>
            `).join('');
        }
        
        function joinStream(streamId) {
            if (streamId === currentStreamId) return;
            
            // Stop current stream if we're streaming
            if (isStreaming) {
                stopStream();
            }
            
            // Close existing connection
            if (socket) {
                socket.close();
            }
            
            currentStreamId = streamId;
            connectToStream(streamId);
            
            // Update UI
            const streamItems = document.querySelectorAll('.stream-item');
            streamItems.forEach(item => item.classList.remove('active'));
            event.target.closest('.stream-item').classList.add('active');
        }
        
        // Auto-refresh streams every 5 seconds
        setInterval(loadStreams, 5000);
    </script>
</body>
</html>
    """
    return HTMLResponse(html_content)


# WebSocket routes
@websocket_route("/ws/viewer/{stream_id}")
async def viewer_websocket(websocket):
    """WebSocket endpoint for viewing streams"""
    await websocket.accept()

    stream_id = websocket.path_params["stream_id"]

    # Add viewer to stream
    if stream_manager.add_viewer(stream_id, websocket):
        try:
            # Send stream info
            stream = stream_manager.get_stream(stream_id)
            if stream:
                await websocket.send_text(
                    json.dumps({"type": "stream_info", "data": stream.get_info()})
                )

            # Keep connection alive
            while True:
                # Wait for messages (mostly for connection keep-alive)
                try:
                    await websocket.receive_text()
                except:
                    break

        except Exception as e:
            print(f"Viewer WebSocket error: {e}")
        finally:
            # Remove viewer when disconnected
            stream_manager.remove_viewer(stream_id, websocket)
    else:
        await websocket.close(code=1000, reason="Stream not found")


# REST API endpoints
async def root(request):
    return ORJSONResponse(
        {
            "message": "Welcome to ZestAPI Video Streaming",
            "version": "1.0.0",
            "endpoints": {
                "interface": "GET /",
                "streams": "GET /api/streams",
                "create_stream": "POST /api/streams",
                "stream_info": "GET /api/streams/{id}",
                "stop_stream": "DELETE /api/streams/{id}",
                "viewer_ws": "ws://localhost:8000/ws/viewer/{stream_id}",
            },
        }
    )


async def list_streams(request):
    """Get list of active streams"""
    streams = stream_manager.list_streams()
    return ORJSONResponse({"streams": streams, "total": len(streams)})


async def get_stream_info(request):
    """Get specific stream information"""
    stream_id = request.path_params["stream_id"]
    stream = stream_manager.get_stream(stream_id)

    if stream:
        return ORJSONResponse(stream.get_info())
    else:
        return ORJSONResponse({"error": "Stream not found"}, status_code=404)


async def create_stream(request):
    """Create a new video stream"""
    try:
        body = await request.json()
        camera_index = body.get("camera_index", 0)
        quality = body.get("quality", "medium")

        stream_id = stream_manager.create_stream(camera_index, quality)
        stream = stream_manager.get_stream(stream_id)

        if stream is None:
            return ORJSONResponse({"error": "Failed to create stream"}, status_code=500)

        return ORJSONResponse(
            {
                "message": "Stream created successfully",
                "stream_id": stream_id,
                **stream.get_info(),
            },
            status_code=201,
        )

    except Exception as e:
        return ORJSONResponse({"error": str(e)}, status_code=400)


async def stop_stream(request):
    """Stop a video stream"""
    stream_id = request.path_params["stream_id"]

    if stream_manager.stop_stream(stream_id):
        return ORJSONResponse({"message": "Stream stopped successfully"})
    else:
        return ORJSONResponse({"error": "Stream not found"}, status_code=404)


async def health_check(request):
    return ORJSONResponse(
        {
            "status": "healthy",
            "service": "zestapi-video-streaming",
            "active_streams": len(stream_manager.streams),
            "total_viewers": sum(
                len(stream.viewers) for stream in stream_manager.streams.values()
            ),
        }
    )


# Add routes
app_instance.add_route("/", video_interface)
app_instance.add_route("/api", root)
app_instance.add_route("/api/streams", list_streams, methods=["GET"])
app_instance.add_route("/api/streams", create_stream, methods=["POST"])
app_instance.add_route("/api/streams/{stream_id}", get_stream_info, methods=["GET"])
app_instance.add_route("/api/streams/{stream_id}", stop_stream, methods=["DELETE"])
app_instance.add_route("/health", health_check)

if __name__ == "__main__":
    print("[*] Starting ZestAPI Video Streaming...")
    print("[*] Open http://localhost:8000 in your browser to start streaming!")
    print("[*] Make sure you have a camera connected and grant camera permissions.")

    try:
        app_instance.run()
    finally:
        # Cleanup streams on shutdown
        stream_manager.cleanup()
