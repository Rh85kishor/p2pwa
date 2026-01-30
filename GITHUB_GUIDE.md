# Quick Guide: Publishing to GitHub

Since Git is not installed in your PATH, here are your options:

## Option 1: Use GitHub Desktop (Easiest)
1. Download GitHub Desktop from https://desktop.github.com/
2. Install it
3. Open GitHub Desktop
4. Click "Add" → "Add Existing Repository"
5. Browse to `C:\p2pwa`
6. Click "Publish repository"
7. Name it "p2pwa" or "p2p-chat-python"
8. Click "Publish"

## Option 2: Use Git Command Line
If you have Git installed but it's not in PATH:

```bash
# Navigate to project
cd C:\p2pwa

# Initialize (if not done)
"C:\Program Files\Git\bin\git.exe" init

# Add all files
"C:\Program Files\Git\bin\git.exe" add .

# Commit
"C:\Program Files\Git\bin\git.exe" commit -m "Initial commit: P2P chat prototype"

# Create repo on GitHub first, then:
"C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/YOUR_USERNAME/p2pwa.git
"C:\Program Files\Git\bin\git.exe" branch -M main
"C:\Program Files\Git\bin\git.exe" push -u origin main
```

## Option 3: Manual Upload
1. Go to https://github.com/new
2. Create a new repository named "p2pwa"
3. Click "uploading an existing file"
4. Drag all files from `C:\p2pwa` into the browser
5. Commit changes

## After Publishing

Share the repository URL with your testing partner:
```
https://github.com/YOUR_USERNAME/p2pwa
```

They can then:
```bash
git clone https://github.com/YOUR_USERNAME/p2pwa.git
cd p2pwa
python main.py
```

## Testing Over Internet (Important!)

⚠️ **The current app only works on the same local network.**

For internet testing, you need:
1. **Port Forwarding**: 
   - Log into your router
   - Forward port 5000 to your computer's local IP
   
2. **Use Public IP**:
   - Find your public IP: https://whatismyipaddress.com/
   - Share `YOUR_PUBLIC_IP:5000` instead of local IP

3. **OR Use Ngrok** (easier):
   ```bash
   # Download ngrok from https://ngrok.com/
   ngrok tcp 5000
   # Share the ngrok URL with your friend
   ```
