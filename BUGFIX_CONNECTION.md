# Bug Fix: Connection Error Resolved

## What Was Fixed

**Error**: `Failed to connect to k1: not enough values to unpack (expected 2, got 1)`

**Cause**: Users were entering usernames (like "k1" or "ravi") instead of the required IP:PORT format.

**Solution**: 
1. Added validation to check for correct format before connecting
2. Added clear instructions in the GUI
3. Added a placeholder example in the input field

## Changes Made

### `p2p_client.py`
- Added validation to ensure peer address contains `:` separator
- Better error messages explaining the required format

### `gui.py`
- Added instruction label: "Enter their Peer ID (format: IP:PORT)"
- Added placeholder text: "192.168.1.100:5000"
- Placeholder clears automatically when user clicks the field

## How to Use (Updated)

1. **User A** starts the app, enters username (e.g., "kishor")
2. **User A** copies their Peer ID (e.g., `192.168.1.50:5000`)
3. **User A** sends this ID to User B (via WhatsApp, email, etc.)
4. **User B** starts the app, enters username (e.g., "ravi")
5. **User B** pastes the FULL Peer ID (`192.168.1.50:5000`) in the connect field
6. **User B** clicks "Connect"

## Important Notes

✅ **Correct format**: `192.168.1.100:5000`
❌ **Wrong format**: `k1`, `ravi`, `192.168.1.100` (missing port)

The app will now show a clear error message if you enter the wrong format!
