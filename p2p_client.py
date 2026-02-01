"""
P2P Client using socket-based direct connections
This is a simplified alternative to Jami daemon for demonstration
"""
import socket
import threading
import json
from typing import Callable, Optional
import time


class P2PClient:
    """Simple P2P client using direct socket connections"""
    
    def __init__(self, port: int = 5000):
        self.port = port
        self.username = ""
        self.peer_connections = {}
        self.message_callback: Optional[Callable] = None
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        
    def start(self, username: str):
        """Start the P2P client"""
        self.username = username
        self.running = True
        
        # Start listening server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        
        # Start accept thread
        accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
        accept_thread.start()
        
        print(f"P2P Client started for {username} on port {self.port}")
        
    def get_peer_id(self) -> str:
        """Get this peer's connection string"""
        # In a real implementation, this would be a hash or DHT address
        # For now, return IP:PORT format
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return f"{local_ip}:{self.port}"
        
    def connect_to_peer(self, peer_address: str) -> bool:
        """Connect to a peer using IP:PORT format"""
        try:
            # Validate format
            if ':' not in peer_address:
                raise ValueError("Peer address must be in format IP:PORT (e.g., 192.168.1.100:5000)")
            
            parts = peer_address.split(':')
            if len(parts) != 2:
                raise ValueError("Invalid address format. Use IP:PORT")
            
            host, port_str = parts
            port = int(port_str)
            
            # Create connection
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((host, port))
            
            # Send handshake
            handshake = {
                'type': 'handshake',
                'username': self.username,
                'peer_id': self.get_peer_id()
            }
            peer_socket.send(json.dumps(handshake).encode() + b'\n')
            
            # Store connection
            self.peer_connections[peer_address] = peer_socket
            
            # Start receive thread
            receive_thread = threading.Thread(
                target=self._receive_messages,
                args=(peer_socket, peer_address),
                daemon=True
            )
            receive_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to connect to {peer_address}: {e}")
            return False
            
    def send_message(self, peer_address: str, message: str):
        """Send a message to a connected peer"""
        if peer_address not in self.peer_connections:
            raise ValueError(f"Not connected to {peer_address}")
            
        msg_data = {
            'type': 'message',
            'from': self.username,
            'text': message,
            'timestamp': time.time()
        }
        
        try:
            self.peer_connections[peer_address].send(
                json.dumps(msg_data).encode() + b'\n'
            )
        except Exception as e:
            print(f"Failed to send message: {e}")
            # Remove dead connection
            del self.peer_connections[peer_address]
            
    def set_message_callback(self, callback: Callable):
        """Set callback for incoming messages"""
        self.message_callback = callback
        
    def _accept_connections(self):
        """Accept incoming peer connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"Incoming connection from {address}")
                
                # Start receive thread for this connection
                receive_thread = threading.Thread(
                    target=self._receive_messages,
                    args=(client_socket, f"{address[0]}:{address[1]}"),
                    daemon=True
                )
                receive_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Accept error: {e}")
                    
    def _receive_messages(self, sock: socket.socket, peer_address: str):
        """Receive messages from a peer"""
        buffer = ""
        
        try:
            while self.running:
                data = sock.recv(4096).decode()
                if not data:
                    break
                    
                buffer += data
                
                # Process complete messages (newline-delimited JSON)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        msg = json.loads(line)
                        self._handle_message(msg, peer_address, sock)
                    except json.JSONDecodeError:
                        pass
                        
        except Exception as e:
            print(f"Receive error from {peer_address}: {e}")
        finally:
            sock.close()
            if peer_address in self.peer_connections:
                del self.peer_connections[peer_address]
                
    def _handle_message(self, msg: dict, peer_address: str, sock: socket.socket):
        """Handle incoming message"""
        msg_type = msg.get('type')
        
        if msg_type == 'handshake':
            # Store the connection
            self.peer_connections[peer_address] = sock
            print(f"Handshake from {msg.get('username')}")
            
        elif msg_type == 'message':
            # Deliver to callback
            if self.message_callback:
                self.message_callback(
                    sender=msg.get('from'),
                    text=msg.get('text'),
                    timestamp=msg.get('timestamp')
                )
                
    def stop(self):
        """Stop the P2P client"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for sock in self.peer_connections.values():
            sock.close()
        self.peer_connections.clear()
