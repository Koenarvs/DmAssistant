# main.py
import os
import logging
from dotenv import load_dotenv
import tkinter as tk
from ui import DnDManagerApp
from db import Database
from chat import ChatManager

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Configure centralized logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    # Check for API Keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set.")
        print("Error: OPENAI_API_KEY environment variable not set. Please set it in the .env file.")
        return
    if not anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY environment variable not set.")
        print("Error: ANTHROPIC_API_KEY environment variable not set. Please set it in the .env file.")
        return

    # Initialize Database
    try:
        db = Database()
    except Exception as e:
        logger.error(f"Failed to initialize the database: {e}")
        print(f"Failed to initialize the database: {e}")
        return

    # Initialize ChatManager
    chat_manager = ChatManager(db, openai_api_key, anthropic_api_key)

    # Initialize Tkinter Root
    root = tk.Tk()
    app = DnDManagerApp(root, db, openai_api_key, anthropic_api_key)   # Pass Anthropic API key here
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()