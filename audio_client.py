"""
Audio Calling Module
Handles audio capture and UDP streaming using SoundDevice
"""
import socket
import threading
import sounddevice as sd
import numpy as np
from typing import Optional

class AudioClient:
    """Handles audio streaming via UDP"""
    
    # Audio Configuration
    SAMPLE_RATE = 16000 # 16kHz
    CHANNELS = 1
    BLOCK_SIZE = 1024 # Buffer size
    
    def __init__(self, port: int):
        self.port = port + 2  # Audio port is Chat Port + 2
        self.remote_address: Optional[tuple] = None
        self.running = False
        
        # Audio Interface (controlled via flags)
        self.input_stream = None
        self.output_stream = None
        
        # Sockets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))
        
    def start_call(self, remote_ip: str, remote_port: int):
        """Start audio call with a peer"""
        self.remote_address = (remote_ip, remote_port + 2)
        self.running = True
        
        try:
            # Start threads
            threading.Thread(target=self._audio_loop, daemon=True).start()
            
            print(f"Audio started on port {self.port} -> {self.remote_address}")
            
        except Exception as e:
            print(f"Audio Start Error: {e}")
            self.stop_call()
        
    def stop_call(self):
        """Stop audio call"""
        self.running = False
        if self.input_stream:
            self.input_stream.abort()
        if self.output_stream:
            self.output_stream.abort()
            
    def _audio_loop(self):
        """Combined audio IO loop"""
        
        def callback(indata, outdata, frames, time, status):
            if status:
                print(status)
            
            # 1. Send Microphone Input
            if self.remote_address:
                try:
                    # Convert to bytes
                    data = indata.tobytes()
                    self.socket.sendto(data, self.remote_address)
                except Exception:
                    pass
            
            # 2. Receive Network Audio (Non-blocking check)
            try:
                # Standard socket recv is blocking, so we need to be careful inside callback
                # But typically we read ONE packet per callback frame
                # Ideally, we should use a buffer queue, but for low latency:
                
                # We need to make recv non-blocking or use a separate thread
                pass 
                
            except Exception:
                pass
                
            # For simplicity in 'sounddevice' callback mode, doing network IO is risky.
            # Better approach: Separate threads for Network RX -> Buffer -> Audio Out
            
        # RE-DESIGN FOR ROBUSTNESS: 
        # Use two separate streams to avoid callback complexity
        self._start_threads()
        
    def _start_threads(self):
        """Start Input and Output threads"""
        threading.Thread(target=self._record_loop, daemon=True).start()
        threading.Thread(target=self._play_loop, daemon=True).start()

    def _record_loop(self):
        """Capture microphone and send UDP"""
        with sd.InputStream(samplerate=self.SAMPLE_RATE, blocksize=self.BLOCK_SIZE, channels=self.CHANNELS, dtype='int16') as stream:
            while self.running:
                data, overflowed = stream.read(self.BLOCK_SIZE)
                if self.remote_address:
                    try:
                        self.socket.sendto(data.tobytes(), self.remote_address)
                    except Exception:
                        pass

    def _play_loop(self):
        """Receive UDP and play to speaker"""
        # Create a queue or write directly to stream
        with sd.OutputStream(samplerate=self.SAMPLE_RATE, blocksize=self.BLOCK_SIZE, channels=self.CHANNELS, dtype='int16') as stream:
            while self.running:
                try:
                    data, _ = self.socket.recvfrom(4096)
                    # Convert bytes back to numpy array
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    stream.write(audio_data)
                except Exception as e:
                    if self.running:
                        print(f"Audio play error: {e}")
