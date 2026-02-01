# Troubleshooting: Connection Timeout Error

## Error Message
```
Failed to connect to 192.168.1.100:5000: [WinError 10060] 
A connection attempt failed because the connected party did not properly respond
```

## Common Causes & Solutions

### 1. Wrong IP Address (Most Common)

**Problem**: You're using `192.168.1.100` but that might not be the correct IP.

**Solution**: Use the EXACT Peer ID shown in the other window!

**Example**:
- Alice's window shows: `192.168.1.50:5000` ← Copy THIS exactly
- Don't type `192.168.1.100:5000` manually

---

### 2. Testing on Same Computer

**If both instances are on the SAME computer**, use `localhost`:

**Instance 1** (Alice):
- Shows: `192.168.1.50:5000`

**Instance 2** (Bob):
- **Don't use**: `192.168.1.50:5000`
- **Use instead**: `localhost:5000` or `127.0.0.1:5000`

---

### 3. Windows Firewall Blocking

**Check if firewall is blocking Python**:

1. Press `Windows + R`
2. Type: `firewall.cpl` and press Enter
3. Click "Allow an app through Windows Firewall"
4. Look for "Python" - make sure it's checked for "Private"

**Or run this as Administrator**:
```powershell
New-NetFirewallRule -DisplayName "P2P Chat Python" -Direction Inbound -Program "C:\Python\python.exe" -Action Allow
```
(Adjust the Python path to match your installation)

---

### 4. Different Networks

**Are you testing across different computers?**

Both computers MUST be on the **same Wi-Fi network**!

❌ Won't work:
- Computer A on Wi-Fi "Home"
- Computer B on Wi-Fi "Guest"

✅ Will work:
- Both on Wi-Fi "Home"

---

## Quick Test: Same Computer

Try this to verify the app works:

**Terminal 1**:
```bash
cd C:\p2pwa
python main.py
```
- Username: Alice
- Note the port (e.g., 5000)

**Terminal 2**:
```bash
cd C:\p2pwa  
python main.py
```
- Username: Bob
- Note the port (e.g., 5001)

**In Bob's window, enter**: `localhost:5000`

If this works, the app is fine - the issue is network/firewall related.

---

## Still Not Working?

Try this debug version to see what's happening:
