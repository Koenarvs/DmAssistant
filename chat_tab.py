# chat_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkhtmlview import HTMLLabel
import logging

logger = logging.getLogger(__name__)

class ChatTab(ttk.Frame):
    def __init__(self, parent, chat_manager):
        super().__init__(parent)
        self.chat_manager = chat_manager
        self.chat_messages = []
        self.create_widgets()
        self.create_context_menu()

    def create_widgets(self):
        # Create a frame for chat history and scrollbar
        history_frame = ttk.Frame(self)
        history_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # Create a vertical scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        # Create the Text widget for chat history
        self.chat_history = tk.Text(
            history_frame,
            wrap='word',
            yscrollcommand=scrollbar.set,
            state='disabled',  # Make it read-only
            background="white"
        )
        self.chat_history.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.chat_history.yview)

        # Define tags for formatting
        self.chat_history.tag_configure("You", foreground="blue", font=("Helvetica", 10, "bold"))
        self.chat_history.tag_configure("ChatGPT", foreground="green", font=("Helvetica", 10, "bold"))
        self.chat_history.tag_configure("message", font=("Helvetica", 10))

        # Create a frame for the input area
        input_frame = ttk.Frame(self)
        input_frame.pack(padx=10, pady=(0, 10), fill='x')

        # Text widget for user input with initial height of 5 rows
        self.chat_entry = tk.Text(input_frame, height=5, wrap='word')
        self.chat_entry.pack(side='left', fill='x', expand=True)
        self.chat_entry.bind("<Return>", self.send_chat)
        self.chat_entry.bind("<Shift-Return>", self.new_line)

        # Scrollbar for input Text widget
        input_scrollbar = ttk.Scrollbar(input_frame, orient='vertical', command=self.chat_entry.yview)
        input_scrollbar.pack(side='right', fill='y')
        self.chat_entry.config(yscrollcommand=input_scrollbar.set)

        # Button frame for Send and Clear buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=(0, 10), fill='x')

        # Send button
        send_button = tk.Button(button_frame, text="Send", command=self.send_chat)
        send_button.pack(side='left', padx=(0, 5))

        # Clear History button
        clear_button = tk.Button(button_frame, text="Clear History", command=self.clear_chat_history)
        clear_button.pack(side='left')

    def create_context_menu(self):
        """Creates a right-click context menu for the chat history."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selected_text)
        self.context_menu.add_command(label="Select All", command=self.select_all_text)

        self.chat_history.bind("<Button-3>", self.show_context_menu)  # For Windows
        self.chat_history.bind("<Button-2>", self.show_context_menu)  # For MacOS

    def show_context_menu(self, event):
        """Displays the context menu."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_selected_text(self):
        """Copies the selected text to the clipboard."""
        try:
            selected_text = self.chat_history.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No text selected

    def select_all_text(self):
        """Selects all text in the chat history."""
        self.chat_history.tag_add(tk.SEL, "1.0", tk.END)
        self.chat_history.mark_set(tk.INSERT, "1.0")
        self.chat_history.see(tk.INSERT)

    def append_text(self, message, sender):
        """Append message to the chat history Text widget with formatting."""
        self.chat_history.configure(state='normal')
        self.chat_history.insert('end', f"{sender}: ", sender)
        self.chat_history.insert('end', f"{message}\n\n", "message")  # Added an extra \n for blank line
        self.chat_history.configure(state='disabled')
        self.chat_history.see('end')  # Scroll to the end

    def send_chat(self, event=None):
        try:
            user_input = self.chat_entry.get("1.0", "end-1c").strip()
            if not user_input:
                return "break"
            self.chat_entry.delete("1.0", tk.END)
            self.chat_messages.append(("You", user_input))
            self.append_text(user_input, "You")

            response = self.chat_manager.generate_response(user_input, self.chat_messages)
            self.chat_messages.append(("ChatGPT", response))
            self.append_text(response, "ChatGPT")
        except Exception as e:
            logger.error(f"Error during send_chat: {e}")
            tk.messagebox.showerror("Chat Error", f"An error occurred while sending the chat: {e}")
        return "break"

    def new_line(self, event):
        """Allows multi-line input when Shift+Enter is pressed"""
        return None  # This allows the default behavior of inserting a newline

    def clear_chat_history(self):
        """Clears the chat history from both the display and the stored messages."""
        confirm = messagebox.askyesno("Clear Chat History", "Are you sure you want to clear the chat history?")
        if confirm:
            self.chat_history.configure(state='normal')
            self.chat_history.delete("1.0", tk.END)
            self.chat_history.configure(state='disabled')
            self.chat_messages.clear()
            logger.info("Chat history cleared.")

