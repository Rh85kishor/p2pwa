"""
Main entry point for P2P Chat application
"""
from gui import ChatGUI


def main():
    print("Starting P2P Chat Application...")
    print("Note: This is a prototype using direct socket connections")
    print("For full Jami/OpenDHT functionality, install Jami from jami.net")
    print()
    
    app = ChatGUI()
    app.run()


if __name__ == "__main__":
    main()
