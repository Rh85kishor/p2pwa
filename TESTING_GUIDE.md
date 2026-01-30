# Testing Guide for P2P Chat Application

## Quick Start

### Step 1: Launch the Application
```bash
cd C:\p2pwa
python main.py
```

The GUI window should appear with a "Welcome to P2P Chat" screen.

## Test Scenario 1: Single Machine Test (Localhost)

### Setup
1. **First Instance**: 
   - Run `python main.py`
   - Enter username: "Alice"
   - Click "Start Chatting"
   - Note your Peer ID (will be something like `192.168.1.x:5000`)

2. **Second Instance**:
   - Open a NEW terminal/command prompt
   - Run `python main.py` again
   - Enter username: "Bob"
   - Click "Start Chatting"
   - Note your Peer ID (will be something like `192.168.1.x:5001`)

### Connect
1. In Bob's window:
   - Copy Alice's Peer ID
   - Paste it in the "Connect with a friend" field
   - Click "Connect"

2. Both windows should now show the chat screen

### Test Messages
1. Type "Hello from Bob" in Bob's window → Press Enter
2. Alice should see: "Bob: Hello from Bob"
3. Type "Hi Bob!" in Alice's window → Press Enter
4. Bob should see: "Alice: Hi Bob!"

## Test Scenario 2: Two Different Computers (Same Network)

### Computer A (Alice)
1. Run the app, enter username "Alice"
2. Copy the Peer ID (e.g., `192.168.1.100:5000`)
3. Send this ID to Computer B (via email, text, etc.)

### Computer B (Bob)
1. Run the app, enter username "Bob"
2. Paste Alice's Peer ID in the connect field
3. Click Connect

### Verify
- Both should be able to send/receive messages
- Messages appear instantly (within 1-2 seconds)

## Troubleshooting

### Issue: "Failed to connect to peer"
**Causes:**
- Firewall blocking port 5000
- Incorrect IP address
- Peer not online yet

**Solutions:**
1. Check Windows Firewall:
   ```powershell
   # Run as Administrator
   New-NetFirewallRule -DisplayName "P2P Chat" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
   ```

2. Verify both apps are running and showing "Online" status

3. Make sure both computers are on the same network

### Issue: Port already in use
**Solution:** The second instance will automatically use port 5001, 5002, etc.

### Issue: Can't see messages
**Cause:** Connection dropped

**Solution:** Click "← Back" and reconnect

## Expected Behavior

✅ **Working correctly if:**
- Both users see "Connected to [peer-address]"
- Messages appear in both windows
- Timestamps are shown
- Can send multiple messages

❌ **Not working if:**
- Connection timeout after 10 seconds
- Messages only appear on sender's side
- "Failed to connect" error

## Network Requirements

- Both computers must be on the same local network (Wi-Fi/Ethernet)
- Port 5000 must be accessible
- No VPN blocking local traffic

## Next Steps After Testing

If the basic version works:
1. We can add encryption (TLS/SSL)
2. Integrate actual Jami daemon
3. Add file transfer
4. Implement group chat
5. Package as standalone .exe

## Known Limitations (Current Version)

- ⚠️ No message history (lost on restart)
- ⚠️ No encryption (messages sent in plain text)
- ⚠️ Only works on local network (no internet routing)
- ⚠️ One-to-one chat only (no groups)

These will be addressed in the Jami-integrated version.
