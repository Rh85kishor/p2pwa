# Quick Fix: Connection Issues

## The Problem
Error: `WinError 10060 - Connection timeout`

This means the peer is not reachable. Here's how to fix it:

---

## Solution 1: Test on Same Computer First

**This is the EASIEST way to verify the app works:**

### Step 1: Open TWO terminals

**Terminal 1** (Alice):
```bash
cd C:\p2pwa
python main.py
```
- Enter username: `Alice`
- You'll see: `P2P Client started for Alice on port 5000`
- Your Peer ID: `192.168.1.x:5000`

**Terminal 2** (Bob):
```bash
cd C:\p2pwa
python main.py
```
- Enter username: `Bob`
- You'll see: `P2P Client started for Bob on port 5001`
- Your Peer ID: `192.168.1.x:5001`

### Step 2: Connect

In **Bob's window**:
- **IMPORTANT**: Don't use Bob's own IP!
- Enter: `localhost:5000` (this connects to Alice on the same computer)
- Click "Connect"

✅ **Should work immediately!**

---

## Solution 2: Different Computers (Same Network)

### Requirements
- Both computers on SAME Wi-Fi network
- Windows Firewall allows Python

### Computer A Steps:
1. Run the app
2. Note the EXACT Peer ID (e.g., `192.168.1.50:5000`)
3. Send this to Computer B (WhatsApp, email, etc.)

### Computer B Steps:
1. Run the app
2. Paste the EXACT Peer ID from Computer A
3. Click Connect

### If Still Fails - Check Firewall:

**Run as Administrator**:
```powershell
# Allow Python through firewall
New-NetFirewallRule -DisplayName "P2P Chat" -Direction Inbound -Protocol TCP -LocalPort 5000-5010 -Action Allow
```

---

## Common Mistakes

❌ **Wrong**: Using the placeholder `192.168.1.100:5000`
✅ **Right**: Copy the ACTUAL Peer ID from the other window

❌ **Wrong**: Different Wi-Fi networks
✅ **Right**: Both on same network

❌ **Wrong**: Typing IP manually
✅ **Right**: Copy-paste the exact Peer ID

---

## Test Right Now

Try the "Same Computer" test above. If that works, the app is fine - it's just a network/firewall issue for cross-computer connections.
