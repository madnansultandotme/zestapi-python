# Video Streaming Application

A real-time video streaming application built with ZestAPI demonstrating WebSocket-based video transmission.

## Features

- **Real-time Video Streaming**: Stream camera feed via WebSockets
- **Multiple Stream Support**: Support for multiple simultaneous streams
- **Frame Rate Control**: Adjustable frame rate and quality
- **Multiple Viewers**: Multiple clients can view the same stream
- **Stream Management**: Start/stop streams, list active streams
- **Quality Settings**: Adjustable video quality and compression
- **Browser-based Viewer**: HTML5 video player interface
- **Stream Recording**: Optional recording capability

## Architecture

### Components
- **Stream Producer**: Camera capture and frame encoding
- **WebSocket Server**: Real-time frame transmission
- **Stream Manager**: Handle multiple streams and viewers
- **Web Interface**: Browser-based video player

### WebSocket Events
- `start_stream` - Start a new video stream
- `stop_stream` - Stop video stream
- `join_stream` - Join as viewer
- `leave_stream` - Leave stream
- `frame_data` - Video frame transmission
- `stream_info` - Stream metadata

## Installation

```bash
cd examples/video-streaming
pip install -r requirements.txt
```

## Requirements

- **Camera**: Webcam or external camera
- **OpenCV**: For video capture and processing
- **Browser**: Modern browser with WebSocket support

## Running

```bash
python main.py
```

The streaming application will be available at `http://localhost:8000`

## Usage

### Starting a Stream
1. Open `http://localhost:8000` in your browser
2. Click "Start Stream" to begin camera capture
3. Adjust quality settings if needed
4. Share the stream URL with viewers

### Viewing a Stream
1. Open the stream URL in your browser
2. Select the stream from the available list
3. Video will start playing automatically

### Stream Controls
- **Quality**: Low (320p), Medium (480p), High (720p)
- **Frame Rate**: 15, 24, 30 FPS
- **Compression**: JPEG quality (50-95%)

## API Endpoints

### REST API
- `GET /` - Web interface
- `GET /api/streams` - List active streams
- `GET /api/streams/{stream_id}` - Get stream info
- `POST /api/streams` - Create new stream
- `DELETE /api/streams/{stream_id}` - Stop stream

### WebSocket
- `ws://localhost:8000/ws/stream/{stream_id}` - Stream endpoint
- `ws://localhost:8000/ws/viewer/{stream_id}` - Viewer endpoint

## Frame Format

Video frames are transmitted as base64-encoded JPEG images:

```json
{
  "type": "frame",
  "data": {
    "stream_id": "stream_123",
    "timestamp": 1234567890,
    "frame": "base64_encoded_jpeg_data",
    "frame_number": 42,
    "quality": "medium"
  }
}
```

## Technical Details

### Video Capture
- Uses OpenCV for camera access
- Supports multiple camera indices
- Configurable resolution and frame rate
- Automatic fallback to available cameras

### Frame Processing
- JPEG compression for efficient transmission
- Configurable quality levels
- Frame skipping for bandwidth management
- Adaptive quality based on connection

### WebSocket Communication
- Binary frame transmission for efficiency
- JSON metadata for frame info
- Automatic reconnection handling
- Bandwidth monitoring

## Performance Considerations

### Bandwidth Usage
- **Low Quality (320p)**: ~500 KB/s per viewer
- **Medium Quality (480p)**: ~1 MB/s per viewer  
- **High Quality (720p)**: ~2 MB/s per viewer

### Scalability
- Single server handles 10-20 concurrent viewers
- Use load balancer for more viewers
- Consider WebRTC for peer-to-peer streaming
- Use CDN for global distribution

## Production Deployment

For production use:
- Use HTTPS/WSS for secure transmission
- Implement authentication and authorization
- Add stream recording capabilities
- Monitor bandwidth and performance
- Implement proper error handling
- Add stream quality adaptation
- Use professional streaming protocols (RTMP, WebRTC)
- Add stream analytics and monitoring

## Security Notes

- Camera access requires HTTPS in production
- Implement proper access controls
- Validate all incoming data
- Monitor for abuse and bandwidth limits
- Consider encryption for sensitive streams
