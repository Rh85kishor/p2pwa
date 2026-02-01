# Port Auto-Increment Test

## What Was Fixed

**Problem**: Both instances were using port 5000 because `SO_REUSEADDR` was allowing port reuse.

**Solution**: Removed `SO_REUSEADDR` during the port search phase so the app properly detects when a port is in use.

## Test It Now

### Terminal 1:
```bash
cd C:\p2pwa
python main.py
```

You should see:
```
P2P Client started for Alice on port 5000
```

### Terminal 2 (while Terminal 1 is still running):
```bash
cd C:\p2pwa
python main.py
```

You should now see:
```
P2P Client started for Bob on port 5001
```
(Note: **5001**, not 5000!)

### Terminal 3 (optional):
```bash
cd C:\p2pwa
python main.py
```

Should show:
```
P2P Client started for Charlie on port 5002
```

## Expected Output

✅ **Correct** (after fix):
- Instance 1: Port 5000
- Instance 2: Port 5001  
- Instance 3: Port 5002

❌ **Wrong** (before fix):
- Instance 1: Port 5000
- Instance 2: Port 5000 (same!)
- Instance 3: Port 5000 (same!)

## Verify in GUI

Each instance should show a different Peer ID:
- Alice: `192.168.1.x:5000`
- Bob: `192.168.1.x:5001`
- Charlie: `192.168.1.x:5002`

**Try it now!**
