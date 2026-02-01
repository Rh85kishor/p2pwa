"""
P2P Client using socket-based direct connections
This is a simplified alternative to Jami daemon for demonstration
"""
import socket
import threading
import json
from typing import Callable, Optional
import time
from peer_discovery import PeerDiscovery


class P2PClient:
    """Simple P2P client using direct socket connections"""
    
    def __init__(self, port: int = 5000):
        self.port = port
        self.username = ""
        self.peer_connections = {}
        self.message_callback: Optional[Callable] = None
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.discovery: Optional[PeerDiscovery] = None
        self.peer_list_callback: Optional[Callable] = None
        
    def start(self, username: str, mobile_number: str = "Unknown"):
        """Start the P2P client"""
        self.username = username
        self.running = True
        
        # Try to bind to the port, increment if already in use
        max_attempts = 10
        bound = False
        
        for attempt in range(max_attempts):
            try:
                current_port = self.port + attempt
                
                # Create new socket for each attempt
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Don't use SO_REUSEADDR during port search - we want to detect conflicts
                test_socket.bind(('0.0.0.0', current_port))
                
                # Port is available, use it
                self.server_socket = test_socket
                self.port = current_port
                bound = True
                break
                
            except OSError as e:
                # Port in use, try next one
                if hasattr('test_socket', 'close'):
                    test_socket.close()
                if attempt == max_attempts - 1:
                    raise RuntimeError(f"Could not find available port in range {self.port}-{self.port + max_attempts}")
                continue
        
        if not bound:
            raise RuntimeError("Failed to bind to any port")
        
        self.server_socket.listen(5)
        
        # Start accept thread
        accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
        accept_thread.start()
        
        # Start peer discovery
        self.discovery = PeerDiscovery(username, self.port)
        self.discovery.set_peer_update_callback(self._on_peer_list_update)
        self.discovery.start()
        
        # Log User Tracking Details
        try:
            with open("tracking_log.txt", "a") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} | Mobile: {mobile_number} | User: {username} | Port: {self.port}\n")
        except Exception as e:
            print(f"Logging error: {e}")
        
        print(f"P2P Client started for {username} (Mobile: {mobile_number}) on port {self.port}")
        
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
            
            # Create connection with timeout
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.settimeout(5)  # 5 second timeout
            
            try:
                peer_socket.connect((host, port))
                peer_socket.settimeout(None)  # Remove timeout after connection
            except socket.timeout:
                raise ConnectionError(f"Connection timeout. Is {host}:{port} reachable?")
            except ConnectionRefusedError:
                raise ConnectionError(f"Connection refused. Is the peer running on {host}:{port}?")
            except OSError as e:
                if "10060" in str(e):
                    raise ConnectionError(f"Network timeout. Check:\n1. Is peer online?\n2. Same network?\n3. Firewall blocking?")
                raise
            
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
    
    def connect_by_username(self, username: str) -> bool:
        """Connect to a peer by username (uses discovery)"""
        if not self.discovery:
            raise RuntimeError("Discovery not initialized")
            
        peer_address = self.discovery.get_peer_address(username)
        if not peer_address:
            raise ValueError(f"Peer '{username}' not found. Are they online?")
            
        return self.connect_to_peer(peer_address)
    
    def get_discovered_peers(self) -> dict:
        """Get list of discovered peers {username: 'ip:port'}"""
        if not self.discovery:
            return {}
        return self.discovery.get_peers()
    
    def set_peer_list_callback(self, callback: Callable):
        """Set callback for when peer list updates"""
        self.peer_list_callback = callback
    
    def _on_peer_list_update(self):
        """Internal callback when peer list changes"""
        if self.peer_list_callback:
            self.peer_list_callback()
            
    def send_message(self, peer_address: str, message: str, msg_type: str = 'message'):
        """Send a message to a connected peer"""
        if peer_address not in self.peer_connections:
            raise ValueError(f"Not connected to {peer_address}")
            
        msg_data = {
            'type': msg_type,
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
            
    def send_group_message(self, message: str):
        """Send a message to all connected peers"""
        if not self.peer_connections:
            return 0
            
        msg_data = {
            'type': 'group_message',
            'from': self.username,
            'text': message,
            'timestamp': time.time()
        }
        
        encoded_msg = json.dumps(msg_data).encode() + b'\n'
        count = 0
        
        # Iterate copy of values to avoid modification issues
        for peer_addr, sock in list(self.peer_connections.items()):
            try:
                sock.send(encoded_msg)
                count += 1
            except Exception as e:
                print(f"Group send error to {peer_addr}: {e}")
                
        return count

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
                        
        elif msg_type == 'group_message':
            # Deliver to callback with special type
            if self.message_callback:
                self.message_callback(
                    sender=msg.get('from'),
                    text=msg.get('text'),
                    timestamp=msg.get('timestamp'),
                    msg_type='group_message'
                )
                
        elif msg_type == 'video_request':
            # New video call request
            if self.message_callback:
                # We use the message callback with a special prefix or add a new callback
                # For simplicity, pass as a system message or separate event
                self.message_callback(
                    sender=msg.get('from'),
                    text="Incoming Video Call... ",
                    timestamp=msg.get('timestamp'),
                    msg_type='video_request',
                    peer_address=peer_address
                )

        elif msg_type == 'audio_request':
            # New audio request
            if self.message_callback:
                self.message_callback(
                    sender=msg.get('from'),
                    text="Incoming Voice Call...",
                    timestamp=msg.get('timestamp'),
                    msg_type='audio_request',
                    peer_address=peer_address
                )
                
    def stop(self):
        """Stop the P2P client"""
        self.running = False
        if self.discovery:
            self.discovery.stop()
        if self.server_socket:
            self.server_socket.close()
        for sock in self.peer_connections.values():
            sock.close()
        self.peer_connections.clear()
