"""
Video Calling Module
Handles video capture and UDP streaming
"""
import cv2
import socket
import threading
import time
import struct
import numpy as np
from PIL import Image, ImageTk
from typing import Optional, Callable

class VideoClient:
    """Handles video streaming via UDP"""
    
    def __init__(self, port: int):
        self.port = port + 1  # Video port is Chat Port + 1
        self.remote_address: Optional[tuple] = None
        self.running = False
        self.capture: Optional[cv2.VideoCapture] = None
        
        # Sockets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)  # 64KB buffer
        self.socket.bind(('0.0.0.0', self.port))
        
        # State
        self.frame_callback: Optional[Callable] = None
        
    def start_call(self, remote_ip: str, remote_port: int, on_frame: Callable):
        """Start video call with a peer"""
        # Video port is always Chat Port + 1
        self.remote_address = (remote_ip, remote_port + 1)
        self.frame_callback = on_frame
        self.running = True
        
        # Initialize camera
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        
        # Start threads
        threading.Thread(target=self._send_loop, daemon=True).start()
        threading.Thread(target=self._receive_loop, daemon=True).start()
        
        print(f"Video started on port {self.port} -> {self.remote_address}")
        
    def stop_call(self):
        """Stop video call"""
        self.running = False
        if self.capture:
            self.capture.release()
        
        # Don't close socket to allow reuse or restart
        # But for full cleanup:
        # self.socket.close() 

    def _send_loop(self):
        """Capture and send frames"""
        while self.running and self.capture.isOpened():
            ret, frame = self.capture.read()
            if not ret:
                continue
                
            # Compress frame
            # 1. Resize (optional, already set in cap props, but safety check)
            frame = cv2.resize(frame, (320, 240))
            
            # 2. Encode to JPEG
            encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            
            # 3. Send via UDP
            if self.remote_address:
                try:
                    # UDP packet limit is ~65KB, our frames should be ~5-10KB
                    message = buffer.tobytes()
                    self.socket.sendto(message, self.remote_address)
                except Exception as e:
                    print(f"Video send error: {e}")
            
            # Limit FPS to ~15 to save bandwidth
            time.sleep(0.066)

    def _receive_loop(self):
        """Receive and decode frames"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(65536)  # Max UDP packet size
                
                # Decode JPEG
                np_data = np.frombuffer(data, dtype=np.uint8)
                frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Convert to Tkinter compatible format
                    # OpenCV is BGR, Pillow uses RGB
                    color_converted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(color_converted)
                    
                    if self.frame_callback:
                        self.frame_callback(pil_image)
                        
            except Exception as e:
                if self.running:
                    print(f"Video receive error: {e}")
