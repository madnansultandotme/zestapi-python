import asyncio
import base64
import json
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import cv2


class VideoStream:
    def __init__(self, stream_id: str, camera_index: int = 0, quality: str = "medium"):
        self.stream_id = stream_id
        self.camera_index = camera_index
        self.quality = quality
        self.is_active = False
        self.viewers: Set[Any] = set()  # WebSocket connections
        self.frame_count = 0
        self.start_time = None
        self.cap = None
        self.streaming_thread = None

        # Quality settings
        self.quality_settings = {
            "low": {"width": 320, "height": 240, "fps": 15, "jpeg_quality": 50},
            "medium": {"width": 640, "height": 480, "fps": 24, "jpeg_quality": 70},
            "high": {"width": 1280, "height": 720, "fps": 30, "jpeg_quality": 85},
        }

        self.settings = self.quality_settings.get(
            quality, self.quality_settings["medium"]
        )

    def start(self) -> bool:
        """Start video capture and streaming"""
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                return False

            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings["width"])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings["height"])
            self.cap.set(cv2.CAP_PROP_FPS, self.settings["fps"])

            self.is_active = True
            self.start_time = datetime.utcnow()

            # Start streaming thread
            self.streaming_thread = threading.Thread(target=self._stream_loop)
            self.streaming_thread.daemon = True
            self.streaming_thread.start()

            return True
        except Exception as e:
            print(f"Failed to start stream {self.stream_id}: {e}")
            return False

    def stop(self):
        """Stop video capture and streaming"""
        self.is_active = False

        if self.cap:
            self.cap.release()
            self.cap = None

        if self.streaming_thread:
            self.streaming_thread.join(timeout=2)

    def add_viewer(self, websocket):
        """Add a viewer to the stream"""
        self.viewers.add(websocket)

    def remove_viewer(self, websocket):
        """Remove a viewer from the stream"""
        self.viewers.discard(websocket)

    def get_info(self) -> Dict[str, Any]:
        """Get stream information"""
        return {
            "stream_id": self.stream_id,
            "quality": self.quality,
            "is_active": self.is_active,
            "viewer_count": len(self.viewers),
            "frame_count": self.frame_count,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "settings": self.settings,
        }

    def _stream_loop(self):
        """Main streaming loop"""
        frame_interval = 1.0 / self.settings["fps"]

        while self.is_active and self.cap and self.cap.isOpened():
            try:
                # Capture frame
                ret, frame = self.cap.read()
                if not ret:
                    break

                # Resize frame if needed
                if (
                    frame.shape[1] != self.settings["width"]
                    or frame.shape[0] != self.settings["height"]
                ):
                    frame = cv2.resize(
                        frame, (self.settings["width"], self.settings["height"])
                    )

                # Encode frame to JPEG
                encode_params = [
                    cv2.IMWRITE_JPEG_QUALITY,
                    self.settings["jpeg_quality"],
                ]
                _, buffer = cv2.imencode(".jpg", frame, encode_params)

                # Convert to base64
                frame_base64 = base64.b64encode(buffer).decode("utf-8")

                # Create frame message
                frame_message = {
                    "type": "frame",
                    "data": {
                        "stream_id": self.stream_id,
                        "timestamp": time.time(),
                        "frame": frame_base64,
                        "frame_number": self.frame_count,
                        "quality": self.quality,
                    },
                }

                self.frame_count += 1

                # Send to all viewers
                asyncio.run(self._broadcast_frame(frame_message))

                # Control frame rate
                time.sleep(frame_interval)

            except Exception as e:
                print(f"Error in streaming loop: {e}")
                break

    async def _broadcast_frame(self, frame_message: Dict):
        """Broadcast frame to all viewers"""
        if not self.viewers:
            return

        message_json = json.dumps(frame_message)
        disconnected_viewers = []

        for viewer in self.viewers.copy():
            try:
                await viewer.send_text(message_json)
            except Exception:
                disconnected_viewers.append(viewer)

        # Remove disconnected viewers
        for viewer in disconnected_viewers:
            self.viewers.discard(viewer)


class StreamManager:
    def __init__(self):
        self.streams: Dict[str, VideoStream] = {}
        self.stream_counter = 0

    def create_stream(self, camera_index: int = 0, quality: str = "medium") -> str:
        """Create a new video stream"""
        self.stream_counter += 1
        stream_id = f"stream_{self.stream_counter}"

        stream = VideoStream(stream_id, camera_index, quality)
        if stream.start():
            self.streams[stream_id] = stream
            return stream_id
        else:
            raise Exception("Failed to start camera")

    def stop_stream(self, stream_id: str) -> bool:
        """Stop a video stream"""
        if stream_id in self.streams:
            self.streams[stream_id].stop()
            del self.streams[stream_id]
            return True
        return False

    def get_stream(self, stream_id: str) -> Optional[VideoStream]:
        """Get a video stream by ID"""
        return self.streams.get(stream_id)

    def list_streams(self) -> List[Dict[str, Any]]:
        """Get list of all streams"""
        return [stream.get_info() for stream in self.streams.values()]

    def add_viewer(self, stream_id: str, websocket) -> bool:
        """Add viewer to a stream"""
        stream = self.get_stream(stream_id)
        if stream:
            stream.add_viewer(websocket)
            return True
        return False

    def remove_viewer(self, stream_id: str, websocket) -> bool:
        """Remove viewer from a stream"""
        stream = self.get_stream(stream_id)
        if stream:
            stream.remove_viewer(websocket)
            return True
        return False

    def cleanup(self):
        """Stop all streams"""
        for stream in self.streams.values():
            stream.stop()
        self.streams.clear()
