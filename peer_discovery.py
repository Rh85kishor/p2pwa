"""
Peer Discovery Module
Uses UDP broadcast to discover peers on local network
"""
import socket
import json
import threading
import time
from typing import Dict, Optional, Callable


class PeerDiscovery:
    """Handles peer discovery via UDP broadcast"""
    
    BROADCAST_PORT = 5555
    BROADCAST_INTERVAL = 5  # seconds
    PEER_TIMEOUT = 15  # seconds - remove peers not seen in this time
    
    def __init__(self, username: str, tcp_port: int):
        self.username = username
        self.tcp_port = tcp_port
        self.peers: Dict[str, dict] = {}  # {username: {ip, port, last_seen}}
        self.running = False
        self.broadcast_socket: Optional[socket.socket] = None
        self.listen_socket: Optional[socket.socket] = None
        self.peer_update_callback: Optional[Callable] = None
        
    def start(self):
        """Start discovery service"""
        self.running = True
        
        # Setup broadcast socket
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Setup listen socket
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(('', self.BROADCAST_PORT))
        
        # Start threads
        threading.Thread(target=self._broadcast_loop, daemon=True).start()
        threading.Thread(target=self._listen_loop, daemon=True).start()
        threading.Thread(target=self._cleanup_loop, daemon=True).start()
        
        print(f"Peer discovery started for {self.username}")
        
    def stop(self):
        """Stop discovery service"""
        self.running = False
        if self.broadcast_socket:
            self.broadcast_socket.close()
        if self.listen_socket:
            self.listen_socket.close()
            
    def set_peer_update_callback(self, callback: Callable):
        """Set callback for when peer list updates"""
        self.peer_update_callback = callback
        
    def get_peers(self) -> Dict[str, str]:
        """Get current peers as {username: 'ip:port'}"""
        return {
            username: f"{info['ip']}:{info['port']}"
            for username, info in self.peers.items()
            if username != self.username  # Don't include self
        }
        
    def get_peer_address(self, username: str) -> Optional[str]:
        """Get IP:PORT for a specific username"""
        if username in self.peers:
            info = self.peers[username]
            return f"{info['ip']}:{info['port']}"
        return None
        
    def _broadcast_loop(self):
        """Periodically broadcast our presence"""
        while self.running:
            try:
                message = json.dumps({
                    'username': self.username,
                    'port': self.tcp_port
                })
                
                self.broadcast_socket.sendto(
                    message.encode('utf-8'),
                    ('<broadcast>', self.BROADCAST_PORT)
                )
                
            except Exception as e:
                print(f"Broadcast error: {e}")
                
            time.sleep(self.BROADCAST_INTERVAL)
            
    def _listen_loop(self):
        """Listen for peer announcements"""
        while self.running:
            try:
                data, addr = self.listen_socket.recvfrom(1024)
                message = json.loads(data.decode('utf-8'))
                
                username = message.get('username')
                port = message.get('port')
                
                if username and port and username != self.username:
                    # Update peer info
                    ip = addr[0]
                    
                    # Check if this is a new peer or updated info
                    is_new = username not in self.peers
                    
                    self.peers[username] = {
                        'ip': ip,
                        'port': port,
                        'last_seen': time.time()
                    }
                    
                    if is_new:
                        print(f"Discovered peer: {username} at {ip}:{port}")
                        
                    # Notify callback
                    if self.peer_update_callback:
                        self.peer_update_callback()
                        
            except Exception as e:
                if self.running:  # Only log if we're supposed to be running
                    print(f"Listen error: {e}")
                    
    def _cleanup_loop(self):
        """Remove stale peers"""
        while self.running:
            try:
                current_time = time.time()
                stale_peers = [
                    username for username, info in self.peers.items()
                    if current_time - info['last_seen'] > self.PEER_TIMEOUT
                ]
                
                for username in stale_peers:
                    print(f"Peer timeout: {username}")
                    del self.peers[username]
                    
                    # Notify callback
                    if self.peer_update_callback:
                        self.peer_update_callback()
                        
            except Exception as e:
                print(f"Cleanup error: {e}")
                
            time.sleep(5)  # Check every 5 seconds
