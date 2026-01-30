# Jami-Inspired P2P Chat (Python Prototype)

A Windows desktop application demonstrating P2P messaging without central servers.

## Features

- ✅ Direct peer-to-peer connections (no central server)
- ✅ Real-time messaging
- ✅ Custom usernames
- ✅ Simple Tkinter GUI
- ✅ Works across local networks

## Important Note

**Jami is not currently installed on this system.** This prototype uses an alternative P2P approach that demonstrates the same concepts:
- Direct peer-to-peer connections
- No message storage on servers
- Distributed architecture

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows OS (tested on Windows 10/11)

### Installation
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/p2pwa.git
cd p2pwa

# Run the application
python main.py
```

## Testing with Others

### Same Network (LAN)
1. Both users run `python main.py`
2. User A copies their Peer ID (e.g., `192.168.1.100:5000`)
3. User B pastes it and clicks "Connect"
4. Start chatting!

### Different Networks (Internet)
⚠️ **Current limitation**: This version only works on the same local network.

For internet connectivity, you'll need:
- Port forwarding on your router (forward port 5000)
- Use your public IP address instead of local IP
- OR install actual Jami for true P2P over internet

## Architecture

This prototype uses:
- **Direct TCP sockets** for P2P networking
- **Tkinter** for GUI
- **Threading** for concurrent connections

## Next Steps

To use actual Jami daemon:
1. Download and install Jami from https://jami.net
2. Locate `jamid.exe` (usually in `C:\Program Files\Jami\daemon`)
3. We can update `p2p_client.py` to use Jami's OpenDHT

## Contributing

Want to help test? 
1. Fork this repo
2. Run the app
3. Report issues or suggest features

## License

MIT License - Feel free to use and modify!

