"""
GUI for P2P Chat Application
Simple Tkinter-based interface
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from p2p_client import P2PClient
import threading


class ChatGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("P2P Chat (Jami-Inspired)")
        self.root.geometry("500x600")
        self.root.configure(bg='#1e1b4b')
        
        self.client: P2PClient = None
        self.current_peer = None
        self.screen = "setup"  # setup, connect, chat
        
        self.setup_styles()
        self.show_setup_screen()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TButton', 
                       background='#6366f1',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=10)
        style.map('TButton',
                 background=[('active', '#4f46e5')])
        
        style.configure('TEntry',
                       fieldbackground='#312e81',
                       foreground='white',
                       borderwidth=1)
        
    def clear_screen(self):
        """Clear all widgets"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
    def show_setup_screen(self):
        """Show username setup screen"""
        self.clear_screen()
        self.screen = "setup"
        
        frame = tk.Frame(self.root, bg='#1e1b4b')
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(frame, text="Welcome to P2P Chat", 
                font=('Arial', 20, 'bold'),
                bg='#1e1b4b', fg='white').pack(pady=20)
        
        tk.Label(frame, text="Choose your display name:",
                font=('Arial', 12),
                bg='#1e1b4b', fg='#94a3b8').pack(pady=10)
        
        self.username_entry = ttk.Entry(frame, width=30, font=('Arial', 12))
        self.username_entry.pack(pady=5)
        self.username_entry.focus()
        
        tk.Label(frame, text="Enter Mobile Number:",
                font=('Arial', 12),
                bg='#1e1b4b', fg='#94a3b8').pack(pady=10)
                
        self.mobile_entry = ttk.Entry(frame, width=30, font=('Arial', 12))
        self.mobile_entry.pack(pady=5)
        
        ttk.Button(frame, text="Start Chatting",
                  command=self.start_client).pack(pady=20)
        
    def start_client(self):
        """Initialize P2P client"""
        username = self.username_entry.get().strip()
        mobile = self.mobile_entry.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
            
        if not mobile:
            messagebox.showerror("Error", "Please enter a mobile number")
            return
            
        try:
            self.client = P2PClient()
            self.client.set_message_callback(self.on_message_received)
            self.client.start(username, mobile)
            self.show_connect_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start client: {e}")
            
    def show_connect_screen(self):
        """Show connection dashboard"""
        self.clear_screen()
        self.screen = "connect"
        
        # Header
        header = tk.Frame(self.root, bg='#312e81', height=80)
        header.pack(fill='x')
        
        tk.Label(header, text="P2P Chat", 
                font=('Arial', 16, 'bold'),
                bg='#312e81', fg='white').pack(pady=10)
        
        tk.Label(header, text=f"• Online as {self.client.username}",
                font=('Arial', 10),
                bg='#312e81', fg='#22c55e').pack()
        
        # Content
        content = tk.Frame(self.root, bg='#1e1b4b')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Center the input
        center_frame = tk.Frame(content, bg='#1e1b4b')
        center_frame.place(relx=0.5, rely=0.4, anchor='center')

        tk.Label(center_frame, text="Enter Friend Name:",
                font=('Arial', 12),
                bg='#1e1b4b', fg='white').pack(pady=10)
        
        self.peer_entry = ttk.Entry(center_frame, width=30, font=('Arial', 12))
        self.peer_entry.pack(pady=5)
        self.peer_entry.focus()
        
        ttk.Button(center_frame, text="Connect",
                  command=self.connect_to_peer).pack(pady=20)
                  
        # Discovery runs in background, but we don't display the list anymore
        # self.client.set_peer_list_callback(None)

    def update_peer_list(self):
        """No longer used"""
        pass
            
    def on_peer_select(self, event):
        """No longer used"""
        pass
        
    def connect_to_peer(self):
        """Connect to a peer using username or IP:PORT"""
        target = self.peer_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a username or IP:PORT")
            return
        
        # Clear placeholder if still there
        if target == "192.168.1.100:5000":
            messagebox.showwarning("Invalid Address", "Please use a real username or ID")
            return
            
        try:
            success = False
            
            # Case 1: IP:PORT format
            if ':' in target:
                success = self.client.connect_to_peer(target)
                if success:
                    self.current_peer = target
                    # Display name is same as address
                    self.current_peer_display = target
            
            # Case 2: Username
            else:
                success = self.client.connect_by_username(target)
                if success:
                    # Get the IP for sending messages
                    address = self.client.discovery.get_peer_address(target)
                    self.current_peer = address
                    # Store friendly name for display
                    self.current_peer_display = f"{target} ({address})"
                
            if success:
                self.show_chat_screen()
            else:
                messagebox.showerror("Connection Failed", 
                                   f"Could not connect to '{target}'.\n\n"
                                   "Troubleshooting:\n"
                                   "1. Is the peer online?\n"
                                   "2. Use 'localhost:PORT' if on same computer\n"
                                   "3. Check if firewall is blocking")
                                   
        except ValueError as e:
             messagebox.showerror("Not Found", str(e))
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            
    def show_chat_screen(self):
        """Show chat interface"""
        self.clear_screen()
        self.screen = "chat"
        
        # Header
        header = tk.Frame(self.root, bg='#312e81', height=60)
        header.pack(fill='x')
        
        ttk.Button(header, text="← Back",
                  command=self.show_connect_screen).pack(side='left', padx=10, pady=10)
        
        # Use stored display name or fall back to address
        display_name = getattr(self, 'current_peer_display', self.current_peer)
        
        tk.Label(header, text=f"Connected to {display_name}",
                font=('Arial', 12, 'bold'),
                bg='#312e81', fg='white').pack(side='left')
        
        # Messages area
        self.messages_text = scrolledtext.ScrolledText(
            self.root,
            bg='#1e1b4b',
            fg='white',
            font=('Arial', 10),
            wrap='word'
        )
        self.messages_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Input area
        input_frame = tk.Frame(self.root, bg='#312e81')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        self.message_entry = ttk.Entry(input_frame, font=('Arial', 11))
        self.message_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        self.message_entry.focus()
        
        ttk.Button(input_frame, text="Send",
                  command=self.send_message).pack(side='right', padx=5)
                  
        # Video Call Button
        ttk.Button(input_frame, text="📹 Video",
                  command=self.start_video_call).pack(side='right', padx=5)
        
    def send_message(self):
        """Send a message"""
        message = self.message_entry.get().strip()
        if not message:
            return
            
        try:
            self.client.send_message(self.current_peer, message)
            self.display_message("You", message)
            self.message_entry.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send: {e}")
            
    def on_message_received(self, sender: str, text: str, timestamp: float, msg_type: str = 'message', peer_address: str = None):
        """Callback for incoming messages"""
        if self.screen == "chat":
            if msg_type == 'video_request':
                # Show incoming call alert
                response = messagebox.askyesno("Incoming Video Call", 
                                             f"Video call from {sender}. Accept?")
                if response:
                    self.root.after(0, lambda: self.open_video_window(peer_address))
            else:
                self.root.after(0, lambda: self.display_message(sender, text))
            
    def display_message(self, sender: str, text: str):
        """Display a message in the chat"""
        self.messages_text.insert('end', f"{sender}: {text}\n")
        self.messages_text.see('end')
        
    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Peer ID copied to clipboard!")
        
    def run(self):
        """Start the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def start_video_call(self):
        """Start a video call"""
        if not self.client or not self.current_peer:
            return
            
        # Send video request
        try:
            self.client.send_message(self.current_peer, "Starting Video Call...", msg_type='video_request')
            self.open_video_window(self.current_peer)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start video: {e}")

    def open_video_window(self, peer_address):
        """Open the video call window"""
        from video_client import VideoClient
        from PIL import ImageTk
        
        # Parse IP/Port
        try:
            # Handle "Name (IP:PORT)" format or just "IP:PORT"
            if '(' in peer_address:
                address_part = peer_address.split('(')[1].strip(')')
            else:
                address_part = peer_address
                
            ip, port = address_part.split(':')
            port = int(port)
            
            # Create Window
            video_win = tk.Toplevel(self.root)
            video_win.title(f"Video Call - {peer_address}")
            video_win.geometry("660x520")
            video_win.configure(bg='#1e1b4b')
            
            # Video Frame
            video_label = tk.Label(video_win, bg='black')
            video_label.pack(fill='both', expand=True, padx=10, pady=10)
            
            tk.Label(video_win, text="Waiting for video...", bg='#1e1b4b', fg='white').pack()
            
            # Start Video Client
            # Use local port based on our Chat Port + 1
            # Remote port is Peer Chat Port + 1
            vc = VideoClient(self.client.port)
            
            def on_frame(image):
                # Update UI in main thread
                def _update():
                    if not video_win.winfo_exists():
                        return
                    photo = ImageTk.PhotoImage(image)
                    video_label.config(image=photo)
                    video_label.image = photo # Keep reference
                self.root.after(0, _update)
            
            vc.start_call(ip, port, on_frame)
            
            # Handle close
            def on_close():
                vc.stop_call()
                video_win.destroy()
                
            video_win.protocol("WM_DELETE_WINDOW", on_close)
            
        except Exception as e:
            messagebox.showerror("Video Error", f"Could not start video: {e}")

    def on_closing(self):
        """Handle window close"""
        if self.client:
            self.client.stop()
        self.root.destroy()


if __name__ == "__main__":
    app = ChatGUI()
    app.run()
