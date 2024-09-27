# chat_tab.py
import tkinter as tk
from tkinter import ttk
from tkhtmlview import HTMLLabel
import markdown
import logging

logger = logging.getLogger(__name__)

class ChatTab(ttk.Frame):
    def __init__(self, parent, chat_manager):
        super().__init__(parent)
        self.chat_manager = chat_manager
        self.chat_messages = []
        self.create_widgets()

    def create_widgets(self):
        self.chat_history = HTMLLabel(self, html="<h2>Chat History</h2><hr>", background="white")
        self.chat_history.pack(padx=10, pady=10, fill='both', expand=True)

        self.chat_entry = tk.Entry(self)
        self.chat_entry.pack(padx=10, pady=(0,10), fill='x')
        self.chat_entry.bind("<Return>", self.send_chat)

        send_button = tk.Button(self, text="Send", command=self.send_chat)
        send_button.pack(padx=10, pady=(0,10))

    def send_chat(self, event=None):
        try:
            user_input = self.chat_entry.get()
            if not user_input.strip():
                return
            self.chat_entry.delete(0, tk.END)
            self.chat_messages.append(("You", user_input))
            self.update_chat_history()

            response = self.chat_manager.generate_response(user_input)
            self.chat_messages.append(("ChatGPT", response))
            self.update_chat_history()
        except Exception as e:
            logger.error(f"Error during send_chat: {e}")
            tk.messagebox.showerror("Chat Error", f"An error occurred while sending the chat: {e}")

    def update_chat_history(self):
        try:
            md_content = "## Chat History\n<hr>\n"
            for sender, message in self.chat_messages:
                if sender == "You":
                    md_content += f"**{sender}:** {message}\n\n"
                else:
                    md_content += f"**{sender}:** {message}\n\n"

            html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
            self.chat_history.set_html(html_content)
        except Exception as e:
            logger.error(f"Error updating chat history: {e}")
            tk.messagebox.showerror("Display Error", f"An error occurred while updating chat history: {e}")