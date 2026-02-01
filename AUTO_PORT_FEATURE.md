# Auto Port Assignment - Feature Update

## What Changed

**Problem**: When running multiple instances on the same computer, both tried to use port 5000, causing the second instance to fail.

**Solution**: The app now automatically finds an available port!

## How It Works

1. **First instance**: Tries port 5000 ✅
2. **Second instance**: Port 5000 is taken, automatically tries 5001 ✅
3. **Third instance**: Tries 5002 ✅
4. And so on... (up to port 5009)

## Example

**Before (broken)**:
```
Instance 1: 192.168.1.100:5000 ✅
Instance 2: 192.168.1.100:5000 ❌ (Error: port in use)
```

**After (fixed)**:
```
Instance 1: 192.168.1.100:5000 ✅
Instance 2: 192.168.1.100:5001 ✅
Instance 3: 192.168.1.100:5002 ✅
```

## Testing on Same Computer

Now you can easily test with yourself:

1. **Terminal 1**: Run `python main.py` → Enter "Alice"
   - Peer ID: `192.168.1.100:5000`

2. **Terminal 2**: Run `python main.py` → Enter "Bob"
   - Peer ID: `192.168.1.100:5001` (automatically!)

3. In Bob's window, paste Alice's ID: `192.168.1.100:5000`
4. Click Connect
5. Start chatting with yourself! 🎉

## No Action Needed

This happens automatically - users don't need to configure anything!
