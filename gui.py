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
        self.username_entry.pack(pady=10)
        self.username_entry.focus()
        
        ttk.Button(frame, text="Start Chatting",
                  command=self.start_client).pack(pady=20)
        
    def start_client(self):
        """Initialize P2P client"""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
            
        try:
            self.client = P2PClient()
            self.client.set_message_callback(self.on_message_received)
            self.client.start(username)
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
        
        tk.Label(header, text=f"● Online as {self.client.username}",
                font=('Arial', 10),
                bg='#312e81', fg='#22c55e').pack()
        
        # Content
        content = tk.Frame(self.root, bg='#1e1b4b')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # My ID section
        id_frame = tk.Frame(content, bg='#312e81', relief='raised', bd=1)
        id_frame.pack(fill='x', pady=10)
        
        tk.Label(id_frame, text="Your Peer ID:",
                font=('Arial', 10),
                bg='#312e81', fg='#94a3b8').pack(anchor='w', padx=10, pady=5)
        
        peer_id = self.client.get_peer_id()
        id_text = tk.Text(id_frame, height=2, width=40, 
                         bg='#1e1b4b', fg='white',
                         font=('Courier', 10))
        id_text.insert('1.0', peer_id)
        id_text.config(state='disabled')
        id_text.pack(padx=10, pady=5)
        
        ttk.Button(id_frame, text="Copy ID",
                  command=lambda: self.copy_to_clipboard(peer_id)).pack(pady=5)
        
        # Connect section
        tk.Label(content, text="Connect with a friend",
                font=('Arial', 12),
                bg='#1e1b4b', fg='white').pack(pady=10)
        
        # Instruction label
        tk.Label(content, text="Enter their Peer ID (format: IP:PORT)",
                font=('Arial', 9),
                bg='#1e1b4b', fg='#94a3b8').pack(pady=5)
        
        connect_frame = tk.Frame(content, bg='#1e1b4b')
        connect_frame.pack()
        
        self.peer_entry = ttk.Entry(connect_frame, width=30, font=('Arial', 10))
        self.peer_entry.insert(0, "192.168.1.100:5000")  # Placeholder
        self.peer_entry.bind('<FocusIn>', lambda e: self.peer_entry.delete(0, 'end') if self.peer_entry.get() == "192.168.1.100:5000" else None)
        self.peer_entry.pack(side='left', padx=5)
        
        ttk.Button(connect_frame, text="Connect",
                  command=self.connect_to_peer).pack(side='left')
        
    def connect_to_peer(self):
        """Connect to a peer"""
        peer_address = self.peer_entry.get().strip()
        if not peer_address:
            messagebox.showerror("Error", "Please enter peer address")
            return
            
        if self.client.connect_to_peer(peer_address):
            self.current_peer = peer_address
            self.show_chat_screen()
        else:
            messagebox.showerror("Error", "Failed to connect to peer")
            
    def show_chat_screen(self):
        """Show chat interface"""
        self.clear_screen()
        self.screen = "chat"
        
        # Header
        header = tk.Frame(self.root, bg='#312e81', height=60)
        header.pack(fill='x')
        
        ttk.Button(header, text="← Back",
                  command=self.show_connect_screen).pack(side='left', padx=10, pady=10)
        
        tk.Label(header, text=f"Connected to {self.current_peer}",
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
            
    def on_message_received(self, sender: str, text: str, timestamp: float):
        """Callback for incoming messages"""
        if self.screen == "chat":
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
        
    def on_closing(self):
        """Handle window close"""
        if self.client:
            self.client.stop()
        self.root.destroy()


if __name__ == "__main__":
    app = ChatGUI()
    app.run()
