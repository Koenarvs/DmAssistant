# ui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from chat_tab import ChatTab  # Import the updated ChatTab
from tkhtmlview import HTMLLabel
from PIL import Image, ImageTk, ImageDraw
from chat import ChatManager
from db import Database
from datetime import datetime
from npc_generator import generate_npc
from dungeon_generator import DungeonGenerator
import os
import markdown
import logging
import json
from pathlib import Path
import io

# Configure logger for ui.py
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class DnDManagerApp:
    def __init__(self, root, db, openai_api_key, anthropic_api_key):
        """
        Initializes the application with the root Tkinter window, database connection, and API keys.
        """
        self.root = root
        self.root.title("D&D Manager with ChatGPT and FAISS")
        self.db = db
        try:
            self.chat_manager = ChatManager(self.db, openai_api_key, anthropic_api_key)  # Pass both API keys here
        except Exception as e:
            logger.error(f"Failed to initialize ChatManager: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize ChatManager: {e}")
            self.on_closing()
            return

        try:
            self.load_json_data()
            self.create_widgets()
        except Exception as e:
            logger.error(f"Failed to create widgets: {e}")
            messagebox.showerror("Initialization Error", f"Failed to create widgets: {e}")
            self.on_closing()
            return

        # Initialize message storage for Markdown rendering
        self.chat_messages = []
        self.world_building_contents = {}
        self.session_notes_contents = {}
        self.npc_details_contents = {}
        self.map_display_image = None  # To hold the currently displayed map image

    def load_json_data(self):
        """
        Loads data from the npc_generation_ellium.json file.
        """
        try:
            json_path = 'npc_generation_ellium.json'
            if not os.path.isfile(json_path):
                logger.error(f"JSON file '{json_path}' not found.")
                messagebox.showerror("File Error", f"JSON file '{json_path}' not found.")
                self.on_closing()
                return

            with open(json_path, 'r') as file:
                data = json.load(file)
            self.factions = [faction["name"] for faction in data.get("factions", [])]
            logger.info("Factions loaded successfully from JSON.")
        except Exception as e:
            logger.error(f"Error loading JSON data: {e}")
            messagebox.showerror("JSON Error", f"Failed to load JSON data: {e}")
            self.on_closing()
            raise

    def create_widgets(self):
        """
        Creates the main tabbed interface and initializes each tab.
        """
        try:
            tab_control = ttk.Notebook(self.root)

            # --- Integrate the Updated Chat Tab ---
            self.chat_tab = ChatTab(tab_control, self.chat_manager)
            tab_control.add(self.chat_tab, text='ChatGPT')

            # --- Other Tabs ---
            self.world_tab = ttk.Frame(tab_control)
            tab_control.add(self.world_tab, text='World Building')

            self.session_tab = ttk.Frame(tab_control)
            tab_control.add(self.session_tab, text='Session Notes')

            self.npc_tab = ttk.Frame(tab_control)
            tab_control.add(self.npc_tab, text='NPC Management')

            self.maps_tab = ttk.Frame(tab_control)
            tab_control.add(self.maps_tab, text='Maps')

            tab_control.pack(expand=1, fill='both')

            # Initialize other tabs
            self.create_world_tab()
            self.create_session_tab()
            self.create_npc_tab()
            self.create_maps_tab()
        except Exception as e:
            logger.error(f"Error during widget creation: {e}")
            raise

    # --- Remove or Comment Out the Old Chat Tab Creation ---
    # def create_chat_tab(self):
    #     """
    #     Sets up the ChatGPT interaction interface.
    #     """
    #     try:
    #         # Chat History using HTMLLabel for rich text rendering
    #         self.chat_history = HTMLLabel(self.chat_tab, html="<h2>Chat History</h2><hr>", background="white")
    #         self.chat_history.pack(padx=10, pady=10, fill='both', expand=True)

    #         # Entry Field
    #         self.chat_entry = tk.Entry(self.chat_tab)
    #         self.chat_entry.pack(padx=10, pady=(0, 10), fill='x')
    #         self.chat_entry.bind("<Return>", self.send_chat)

    #         # Send Button
    #         send_button = tk.Button(self.chat_tab, text="Send", command=self.send_chat)
    #         send_button.pack(padx=10, pady=(0, 10))
    #     except Exception as e:
    #         logger.error(f"Error creating Chat Tab: {e}")
    #         raise

    def send_chat(self, event=None):
        """
        Handles sending user input to ChatGPT and displaying the response.
        """
        try:
            user_input = self.chat_entry.get()
            if not user_input.strip():
                return
            self.chat_entry.delete(0, tk.END)
            self.chat_messages.append(("You", user_input))
            self.update_chat_history()

            # Generate response with context using FAISS
            response = self.chat_manager.generate_response(user_input)
            self.chat_messages.append(("ChatGPT", response))
            self.update_chat_history()
        except Exception as e:
            logger.error(f"Error during send_chat: {e}")
            messagebox.showerror("Chat Error", f"An error occurred while sending the chat: {e}")

    def update_chat_history(self):
        """
        Updates the chat history display with new messages using Markdown rendering.
        """
        try:
            # Convert chat messages to Markdown format
            md_content = "## Chat History\n<hr>\n"
            for sender, message in self.chat_messages:
                md_content += f"**{sender}:** {message}\n\n"

            # Convert Markdown to HTML
            html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])

            # Update the HTMLLabel content
            self.chat_history.set_html(html_content)
        except Exception as e:
            logger.error(f"Error updating chat history: {e}")
            messagebox.showerror("Display Error", f"An error occurred while updating chat history: {e}")

    # --- World Building Tab ---
    def create_world_tab(self):
        """
        Sets up the World Building management interface.
        """
        try:
            # Frame for Input
            input_frame = ttk.Frame(self.world_tab)
            input_frame.pack(padx=10, pady=10, fill='x')

            # Title Entry
            ttk.Label(input_frame, text="Title:").grid(row=0, column=0, sticky='w', pady=2)
            self.world_title = ttk.Entry(input_frame)
            self.world_title.grid(row=0, column=1, sticky='ew', pady=2)

            # Content Text
            ttk.Label(input_frame, text="Content (Markdown supported):").grid(row=1, column=0, sticky='nw', pady=2)
            self.world_content_input = tk.Text(input_frame, height=5)
            self.world_content_input.grid(row=1, column=1, sticky='ew', pady=2)

            # Configure grid weights
            input_frame.columnconfigure(1, weight=1)

            # Save Button
            save_button = tk.Button(input_frame, text="Save World Building", command=self.save_world_building)
            save_button.grid(row=2, column=1, sticky='e', pady=10)

            # Edit Button
            edit_button = tk.Button(input_frame, text="Edit Selected", command=self.edit_selected_world)
            edit_button.grid(row=2, column=0, sticky='w', pady=10)

            # Separator
            separator = ttk.Separator(self.world_tab, orient='horizontal')
            separator.pack(fill='x', padx=10, pady=5)

            # Frame for Display
            display_frame = ttk.Frame(self.world_tab)
            display_frame.pack(padx=10, pady=10, fill='both', expand=True)

            # Display Label
            ttk.Label(display_frame, text="Existing World Building Entries:").pack(anchor='w')

            # Listbox for Entries
            self.world_listbox = tk.Listbox(display_frame)
            self.world_listbox.pack(side='left', fill='y', padx=(0, 10), pady=5)
            self.world_listbox.bind('<<ListboxSelect>>', self.display_selected_world)

            # Scrollbar for Listbox
            scrollbar = ttk.Scrollbar(display_frame, orient='vertical', command=self.world_listbox.yview)
            scrollbar.pack(side='left', fill='y')
            self.world_listbox.config(yscrollcommand=scrollbar.set)

            # HTMLLabel for Displaying Content
            self.world_content_display = HTMLLabel(display_frame, html="<h2>World Building Content</h2><hr>", background="white")
            self.world_content_display.pack(side='left', fill='both', expand=True)

            # Populate Listbox
            self.populate_world_listbox()
        except Exception as e:
            logger.error(f"Error creating World Building Tab: {e}")
            raise

    def save_world_building(self):
        """
        Saves a new world building entry to the database and updates the FAISS index.
        """
        try:
            title = self.world_title.get()
            content = self.world_content_input.get("1.0", tk.END).strip()
            if not title or not content:
                messagebox.showwarning("Input Error", "Please provide both title and content.")
                return
            record_id = self.db.add_world_building(title, content)
            messagebox.showinfo("Success", "World building information saved.")
            self.world_title.delete(0, tk.END)
            self.world_content_input.delete("1.0", tk.END)
            # Add the new record to FAISS index incrementally
            new_record = self.db.get_record_by_id('world_building', record_id)
            self.chat_manager.add_record_to_index('world_building', new_record)
            self.populate_world_listbox()
        except Exception as e:
            logger.error(f"Failed to save world building information: {e}")
            messagebox.showerror("Error", f"Failed to save world building information: {str(e)}")

    def populate_world_listbox(self):
        """
        Populates the Listbox with existing world building entries.
        """
        try:
            records = self.db.get_world_building()
            self.world_listbox.delete(0, tk.END)
            for record in records:
                display_text = f"{record[1]}"  # Display the title
                self.world_listbox.insert(tk.END, display_text)
        except Exception as e:
            logger.error(f"Failed to populate world building list: {e}")
            messagebox.showerror("Error", f"Failed to populate world building list: {str(e)}")

    def display_selected_world(self, event):
        """
        Displays the content of the selected world building entry with Markdown rendering.
        """
        try:
            selection = self.world_listbox.curselection()
            if selection:
                index = selection[0]
                records = self.db.get_world_building()
                selected_record = records[index]
                content = selected_record[2]
                # Convert Markdown to HTML
                html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
                # Update the HTMLLabel content
                self.world_content_display.set_html(html_content)
        except Exception as e:
            logger.error(f"Failed to display selected world building entry: {e}")
            messagebox.showerror("Error", f"Failed to display selected world building entry: {str(e)}")

    def edit_selected_world(self):
        """
        Initiates the edit process for the selected world building entry.
        """
        try:
            selection = self.world_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selection Error", "Please select a world building entry to edit.")
                return
            index = selection[0]
            records = self.db.get_world_building()
            selected_record = records[index]
            # Adjusted unpacking to include the 'last_updated' field
            record_id, current_title, current_content, _ = selected_record

            # Create Edit Dialog
            edit_dialog = tk.Toplevel(self.root)
            edit_dialog.title("Edit World Building Entry")

            ttk.Label(edit_dialog, text="Title:").grid(row=0, column=0, sticky='w', pady=2, padx=5)
            title_entry = ttk.Entry(edit_dialog, width=50)
            title_entry.grid(row=0, column=1, pady=2, padx=5)
            title_entry.insert(0, current_title)

            ttk.Label(edit_dialog, text="Content (Markdown supported):").grid(row=1, column=0, sticky='nw', pady=2, padx=5)
            content_text = tk.Text(edit_dialog, width=50, height=10)
            content_text.grid(row=1, column=1, pady=2, padx=5)
            content_text.insert(tk.END, current_content)

            def save_changes():
                try:
                    new_title = title_entry.get().strip()
                    new_content = content_text.get("1.0", tk.END).strip()
                    if not new_title or not new_content:
                        messagebox.showwarning("Input Error", "Please provide both title and content.")
                        return
                    confirm = messagebox.askyesno("Confirm Edit", "Are you sure you want to save these changes?")
                    if confirm:
                        success = self.db.update_world_building(record_id, new_title, new_content)
                        if success:
                            messagebox.showinfo("Success", "World building entry updated successfully.")
                            edit_dialog.destroy()
                            self.populate_world_listbox()
                            # Rebuild FAISS index
                            self.rebuild_faiss_index()
                        else:
                            messagebox.showerror("Error", "Failed to update the world building entry.")
                except Exception as e:
                    logger.error(f"Failed to update world building entry: {e}")
                    messagebox.showerror("Error", f"Failed to update world building entry: {str(e)}")

            save_button = tk.Button(edit_dialog, text="Save Changes", command=save_changes)
            save_button.grid(row=2, column=1, sticky='e', pady=10, padx=5)
        except Exception as e:
            logger.error(f"Failed to initiate edit: {e}")
            messagebox.showerror("Error", f"Failed to initiate edit: {str(e)}")

    # --- Session Notes Tab ---
    def create_session_tab(self):
        """
        Sets up the Session Notes management interface.
        """
        try:
            # Frame for Input
            input_frame = ttk.Frame(self.session_tab)
            input_frame.pack(padx=10, pady=10, fill='x')

            # Date Entry
            ttk.Label(input_frame, text="Date:").grid(row=0, column=0, sticky='w', pady=2)
            self.session_date = ttk.Entry(input_frame)
            self.session_date.grid(row=0, column=1, sticky='ew', pady=2)
            self.session_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

            # Notes Text
            ttk.Label(input_frame, text="Notes (Markdown supported):").grid(row=1, column=0, sticky='nw', pady=2)
            self.session_notes_input = tk.Text(input_frame, height=5)
            self.session_notes_input.grid(row=1, column=1, sticky='ew', pady=2)

            # Configure grid weights
            input_frame.columnconfigure(1, weight=1)

            # Save Button
            save_button = tk.Button(input_frame, text="Save Session Notes", command=self.save_session_notes)
            save_button.grid(row=2, column=1, sticky='e', pady=10)

            # Edit Button
            edit_button = tk.Button(input_frame, text="Edit Selected", command=self.edit_selected_session)
            edit_button.grid(row=2, column=0, sticky='w', pady=10)

            # Separator
            separator = ttk.Separator(self.session_tab, orient='horizontal')
            separator.pack(fill='x', padx=10, pady=5)

            # Frame for Display
            display_frame = ttk.Frame(self.session_tab)
            display_frame.pack(padx=10, pady=10, fill='both', expand=True)

            # Display Label
            ttk.Label(display_frame, text="Existing Session Notes:").pack(anchor='w')

            # Listbox for Entries
            self.session_listbox = tk.Listbox(display_frame)
            self.session_listbox.pack(side='left', fill='y', padx=(0, 10), pady=5)
            self.session_listbox.bind('<<ListboxSelect>>', self.display_selected_session)

            # Scrollbar for Listbox
            scrollbar = ttk.Scrollbar(display_frame, orient='vertical', command=self.session_listbox.yview)
            scrollbar.pack(side='left', fill='y')
            self.session_listbox.config(yscrollcommand=scrollbar.set)

            # HTMLLabel for Displaying Notes
            self.session_notes_display = HTMLLabel(display_frame, html="<h2>Session Notes</h2><hr>", background="white")
            self.session_notes_display.pack(side='left', fill='both', expand=True)

            # Populate Listbox
            self.populate_session_listbox()
        except Exception as e:
            logger.error(f"Error creating Session Notes Tab: {e}")
            raise

    def save_session_notes(self):
        """
        Saves new session notes to the database and updates the FAISS index.
        """
        try:
            date = self.session_date.get()
            notes = self.session_notes_input.get("1.0", tk.END).strip()
            if not date or not notes:
                messagebox.showwarning("Input Error", "Please provide both date and notes.")
                return
            record_id = self.db.add_session_notes(date, notes)
            messagebox.showinfo("Success", "Session notes saved.")
            self.session_notes_input.delete("1.0", tk.END)
            # Add the new record to FAISS index incrementally
            new_record = self.db.get_record_by_id('session_notes', record_id)
            self.chat_manager.add_record_to_index('session_notes', new_record)
            self.populate_session_listbox()
        except Exception as e:
            logger.error(f"Failed to save session notes: {e}")
            messagebox.showerror("Error", f"Failed to save session notes: {str(e)}")

    def populate_session_listbox(self):
        """
        Populates the Listbox with existing session notes entries.
        """
        try:
            records = self.db.get_session_notes()
            self.session_listbox.delete(0, tk.END)
            for record in records:
                display_text = f"{record[1]}"  # Display the date
                self.session_listbox.insert(tk.END, display_text)
        except Exception as e:
            logger.error(f"Failed to populate session notes list: {e}")
            messagebox.showerror("Error", f"Failed to populate session notes list: {str(e)}")

    def display_selected_session(self, event):
        """
        Displays the notes of the selected session entry with Markdown rendering.
        """
        try:
            selection = self.session_listbox.curselection()
            if selection:
                index = selection[0]
                records = self.db.get_session_notes()
                selected_record = records[index]
                notes = selected_record[2]
                # Convert Markdown to HTML
                html_content = markdown.markdown(notes, extensions=['fenced_code', 'tables'])
                # Update the HTMLLabel content
                self.session_notes_display.set_html(html_content)
        except Exception as e:
            logger.error(f"Failed to display selected session note: {e}")
            messagebox.showerror("Error", f"Failed to display selected session note: {str(e)}")

    def edit_selected_session(self):
        """
        Initiates the edit process for the selected session notes entry.
        """
        try:
            selection = self.session_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selection Error", "Please select a session notes entry to edit.")
                return
            index = selection[0]
            records = self.db.get_session_notes()
            selected_record = records[index]
            # Adjusted unpacking to include the 'last_updated' field
            record_id, current_date, current_notes, _ = selected_record

            # Create Edit Dialog
            edit_dialog = tk.Toplevel(self.root)
            edit_dialog.title("Edit Session Notes Entry")

            ttk.Label(edit_dialog, text="Date:").grid(row=0, column=0, sticky='w', pady=2, padx=5)
            date_entry = ttk.Entry(edit_dialog, width=30)
            date_entry.grid(row=0, column=1, pady=2, padx=5)
            date_entry.insert(0, current_date)

            ttk.Label(edit_dialog, text="Notes (Markdown supported):").grid(row=1, column=0, sticky='nw', pady=2, padx=5)
            notes_text = tk.Text(edit_dialog, width=50, height=10)
            notes_text.grid(row=1, column=1, pady=2, padx=5)
            notes_text.insert(tk.END, current_notes)

            def save_changes():
                try:
                    new_date = date_entry.get().strip()
                    new_notes = notes_text.get("1.0", tk.END).strip()
                    if not new_date or not new_notes:
                        messagebox.showwarning("Input Error", "Please provide both date and notes.")
                        return
                    confirm = messagebox.askyesno("Confirm Edit", "Are you sure you want to save these changes?")
                    if confirm:
                        success = self.db.update_session_notes(record_id, new_date, new_notes)
                        if success:
                            messagebox.showinfo("Success", "Session notes entry updated successfully.")
                            edit_dialog.destroy()
                            self.populate_session_listbox()
                            # Rebuild FAISS index
                            self.rebuild_faiss_index()
                        else:
                            messagebox.showerror("Error", "Failed to update the session notes entry.")
                except Exception as e:
                    logger.error(f"Failed to update session notes entry: {e}")
                    messagebox.showerror("Error", f"Failed to update session notes entry: {str(e)}")

            save_button = tk.Button(edit_dialog, text="Save Changes", command=save_changes)
            save_button.grid(row=2, column=1, sticky='e', pady=10, padx=5)
        except Exception as e:
            logger.error(f"Failed to initiate edit: {e}")
            messagebox.showerror("Error", f"Failed to initiate edit: {str(e)}")

    # --- NPC Management Tab ---
    def create_npc_tab(self):
        """
        Sets up the NPC Management interface, including forms to add, edit, delete, and display NPCs.
        """
        try:
            # Frame for NPC Form
            form_frame = ttk.Frame(self.npc_tab)
            form_frame.pack(padx=10, pady=10, fill='x')

            # NPC Name
            ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky='w', pady=2)
            self.npc_name = ttk.Entry(form_frame)
            self.npc_name.grid(row=0, column=1, sticky='ew', pady=2)

            # Race
            ttk.Label(form_frame, text="Race:").grid(row=1, column=0, sticky='w', pady=2)
            self.npc_race = ttk.Entry(form_frame)
            self.npc_race.grid(row=1, column=1, sticky='ew', pady=2)

            # Class
            ttk.Label(form_frame, text="Class:").grid(row=2, column=0, sticky='w', pady=2)
            self.npc_class = ttk.Entry(form_frame)
            self.npc_class.grid(row=2, column=1, sticky='ew', pady=2)

            # Gender
            ttk.Label(form_frame, text="Gender:").grid(row=3, column=0, sticky='w', pady=2)
            self.npc_gender = ttk.Entry(form_frame)
            self.npc_gender.grid(row=3, column=1, sticky='ew', pady=2)

            # Age
            ttk.Label(form_frame, text="Age:").grid(row=4, column=0, sticky='w', pady=2)
            self.npc_age = ttk.Entry(form_frame)
            self.npc_age.grid(row=4, column=1, sticky='ew', pady=2)

            # Appearance
            ttk.Label(form_frame, text="Appearance (Markdown supported):").grid(row=5, column=0, sticky='nw', pady=2)
            self.npc_appearance = tk.Text(form_frame, height=3)
            self.npc_appearance.grid(row=5, column=1, sticky='ew', pady=2)

            # Background
            ttk.Label(form_frame, text="Background (Markdown supported):").grid(row=6, column=0, sticky='nw', pady=2)
            self.npc_background = tk.Text(form_frame, height=3)
            self.npc_background.grid(row=6, column=1, sticky='ew', pady=2)

            # Languages
            ttk.Label(form_frame, text="Languages:").grid(row=7, column=0, sticky='w', pady=2)
            self.npc_languages = ttk.Entry(form_frame)
            self.npc_languages.grid(row=7, column=1, sticky='ew', pady=2)

            # Personality Traits
            ttk.Label(form_frame, text="Personality Traits (Markdown supported):").grid(row=8, column=0, sticky='nw', pady=2)
            self.npc_personality = tk.Text(form_frame, height=3)
            self.npc_personality.grid(row=8, column=1, sticky='ew', pady=2)

            # Ideals
            ttk.Label(form_frame, text="Ideals (Markdown supported):").grid(row=9, column=0, sticky='nw', pady=2)
            self.npc_ideals = tk.Text(form_frame, height=3)
            self.npc_ideals.grid(row=9, column=1, sticky='ew', pady=2)

            # Bonds
            ttk.Label(form_frame, text="Bonds (Markdown supported):").grid(row=10, column=0, sticky='nw', pady=2)
            self.npc_bonds = tk.Text(form_frame, height=3)
            self.npc_bonds.grid(row=10, column=1, sticky='ew', pady=2)

            # Flaws
            ttk.Label(form_frame, text="Flaws (Markdown supported):").grid(row=11, column=0, sticky='nw', pady=2)
            self.npc_flaws = tk.Text(form_frame, height=3)
            self.npc_flaws.grid(row=11, column=1, sticky='ew', pady=2)

            # Backstory
            ttk.Label(form_frame, text="Backstory (Markdown supported):").grid(row=12, column=0, sticky='nw', pady=2)
            self.npc_backstory = tk.Text(form_frame, height=3)
            self.npc_backstory.grid(row=12, column=1, sticky='ew', pady=2)

            # Role in World
            ttk.Label(form_frame, text="Role in World:").grid(row=13, column=0, sticky='w', pady=2)
            self.npc_role = ttk.Entry(form_frame)
            self.npc_role.grid(row=13, column=1, sticky='ew', pady=2)

            # Alignment
            ttk.Label(form_frame, text="Alignment:").grid(row=14, column=0, sticky='w', pady=2)
            self.npc_alignment = ttk.Entry(form_frame)
            self.npc_alignment.grid(row=14, column=1, sticky='ew', pady=2)

            # Deity
            ttk.Label(form_frame, text="Deity:").grid(row=15, column=0, sticky='w', pady=2)
            self.npc_deity = ttk.Entry(form_frame)
            self.npc_deity.grid(row=15, column=1, sticky='ew', pady=2)

            # Faction
            ttk.Label(form_frame, text="Faction:").grid(row=16, column=0, sticky='w', pady=2)
            self.npc_faction = ttk.Entry(form_frame)
            self.npc_faction.grid(row=16, column=1, sticky='ew', pady=2)

            # Image Path
            ttk.Label(form_frame, text="Image Path:").grid(row=17, column=0, sticky='w', pady=2)
            self.npc_image_path = ttk.Entry(form_frame)
            self.npc_image_path.grid(row=17, column=1, sticky='ew', pady=2)
            browse_button = ttk.Button(form_frame, text="Browse", command=self.browse_image)
            browse_button.grid(row=17, column=2, sticky='w', pady=2, padx=5)

            # Configure grid weights
            form_frame.columnconfigure(1, weight=1)

            # Create NPC Button
            create_npc_button = tk.Button(form_frame, text="Create NPC", command=self.create_npc)
            create_npc_button.grid(row=18, column=0, sticky='w', pady=10)

            # Save NPC Button
            save_npc_button = tk.Button(form_frame, text="Add NPC", command=self.add_npc)
            save_npc_button.grid(row=18, column=1, sticky='e', pady=10)

            # Separator
            separator = ttk.Separator(self.npc_tab, orient='horizontal')
            separator.pack(fill='x', padx=10, pady=5)

            # Frame for NPC List
            list_frame = ttk.Frame(self.npc_tab)
            list_frame.pack(padx=10, pady=10, fill='both', expand=True)

            # Display Label
            ttk.Label(list_frame, text="Existing NPCs:").pack(anchor='w')

            # Listbox for NPCs
            self.npc_listbox = tk.Listbox(list_frame)
            self.npc_listbox.pack(side='left', fill='y', padx=(0, 10), pady=5)
            self.npc_listbox.bind('<<ListboxSelect>>', self.display_selected_npc)

            # Scrollbar for Listbox
            scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.npc_listbox.yview)
            scrollbar.pack(side='left', fill='y')
            self.npc_listbox.config(yscrollcommand=scrollbar.set)

            # HTMLLabel for Displaying NPC Details
            self.npc_details_display = HTMLLabel(list_frame, html="<h2>NPC Details</h2><hr>", background="white")
            self.npc_details_display.pack(side='left', fill='both', expand=True)

            # Populate Listbox
            self.populate_npc_listbox()
        except Exception as e:
            logger.error(f"Error creating NPC Management Tab: {e}")
            raise

    def create_npc(self):
        """
        Generates a random NPC and populates the form fields for further editing.
        """
        try:
            npc = generate_npc()

            # Populate form fields with generated data
            self.npc_name.delete(0, tk.END)
            self.npc_name.insert(0, npc.get('name', ''))

            self.npc_race.delete(0, tk.END)
            self.npc_race.insert(0, npc.get('race', ''))

            self.npc_class.delete(0, tk.END)
            self.npc_class.insert(0, npc.get('class', ''))

            self.npc_gender.delete(0, tk.END)
            self.npc_gender.insert(0, npc.get('gender', ''))

            self.npc_age.delete(0, tk.END)
            self.npc_age.insert(0, npc.get('age', ''))

            self.npc_appearance.delete("1.0", tk.END)
            self.npc_appearance.insert(tk.END, npc.get('appearance', ''))

            self.npc_background.delete("1.0", tk.END)
            self.npc_background.insert(tk.END, npc.get('background', ''))

            self.npc_languages.delete(0, tk.END)
            self.npc_languages.insert(0, npc.get('languages', ''))

            self.npc_personality.delete("1.0", tk.END)
            self.npc_personality.insert(tk.END, npc.get('personality_traits', ''))

            self.npc_ideals.delete("1.0", tk.END)
            self.npc_ideals.insert(tk.END, npc.get('ideals', ''))

            self.npc_bonds.delete("1.0", tk.END)
            self.npc_bonds.insert(tk.END, npc.get('bonds', ''))

            self.npc_flaws.delete("1.0", tk.END)
            self.npc_flaws.insert(tk.END, npc.get('flaws', ''))

            self.npc_backstory.delete("1.0", tk.END)
            self.npc_backstory.insert(tk.END, npc.get('backstory', ''))

            self.npc_role.delete(0, tk.END)
            self.npc_role.insert(0, npc.get('role_in_world', ''))

            self.npc_alignment.delete(0, tk.END)
            self.npc_alignment.insert(0, npc.get('alignment', ''))

            self.npc_deity.delete(0, tk.END)
            self.npc_deity.insert(0, npc.get('deity_aspect', ''))

            # Faction as a text field
            faction = npc.get('faction', 'None')
            if faction not in self.factions:
                faction = "None"
            self.npc_faction.delete(0, tk.END)
            self.npc_faction.insert(0, faction)

            self.npc_image_path.delete(0, tk.END)
            self.npc_image_path.insert(0, npc.get('image_path', ''))

            messagebox.showinfo("NPC Created", "A new NPC has been generated. You can edit the details before saving.")
        except Exception as e:
            logger.error(f"Failed to create NPC: {e}")
            messagebox.showerror("Error", f"Failed to create NPC: {str(e)}")

    def browse_image(self):
        """
        Opens a file dialog to select an image for the NPC.
        """
        try:
            file_path = filedialog.askopenfilename(
                title="Select NPC Image",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif"), ("All Files", "*.*")]
            )
            if file_path:
                self.npc_image_path.delete(0, tk.END)
                self.npc_image_path.insert(0, file_path)
        except Exception as e:
            logger.error(f"Error browsing image: {e}")
            messagebox.showerror("Error", f"Failed to browse image: {e}")

    def add_npc(self):
        """
        Collects NPC data from the form and adds it to the database.
        """
        try:
            npc_data = {
                'name': self.npc_name.get(),
                'race': self.npc_race.get(),
                'class': self.npc_class.get(),
                'gender': self.npc_gender.get(),
                'age': int(self.npc_age.get()) if self.npc_age.get().isdigit() else None,
                'appearance': self.npc_appearance.get("1.0", tk.END).strip(),
                'background': self.npc_background.get("1.0", tk.END).strip(),
                'languages': self.npc_languages.get(),
                'personality_traits': self.npc_personality.get("1.0", tk.END).strip(),
                'ideals': self.npc_ideals.get("1.0", tk.END).strip(),
                'bonds': self.npc_bonds.get("1.0", tk.END).strip(),
                'flaws': self.npc_flaws.get("1.0", tk.END).strip(),
                'backstory': self.npc_backstory.get("1.0", tk.END).strip(),
                'role_in_world': self.npc_role.get(),
                'alignment': self.npc_alignment.get(),
                'deity': self.npc_deity.get(),
                'faction_affiliation': self.npc_faction.get(),
                'image_path': self.npc_image_path.get(),
                # Dynamic Information can be added here as needed
            }

            # Basic validation
            if not npc_data['name']:
                messagebox.showwarning("Input Error", "Please provide the NPC's name.")
                return

            # Validate age is numeric
            if npc_data['age'] is None:
                messagebox.showwarning("Input Error", "Age must be a number.")
                return

            npc_id = self.db.add_npc(npc_data)
            messagebox.showinfo("Success", f"NPC '{npc_data['name']}' added successfully.")
            self.clear_npc_form()
            # Add the new NPC to FAISS index incrementally
            new_npc = self.db.get_npc_by_id(npc_id)
            self.chat_manager.add_record_to_index('npc', new_npc)
            self.populate_npc_listbox()
        except Exception as e:
            logger.error(f"Failed to add NPC: {e}")
            messagebox.showerror("Error", f"Failed to add NPC: {str(e)}")

    def clear_npc_form(self):
        """
        Clears all input fields in the NPC form.
        """
        try:
            self.npc_name.delete(0, tk.END)
            self.npc_race.delete(0, tk.END)
            self.npc_class.delete(0, tk.END)
            self.npc_gender.delete(0, tk.END)
            self.npc_age.delete(0, tk.END)
            self.npc_appearance.delete("1.0", tk.END)
            self.npc_background.delete("1.0", tk.END)
            self.npc_languages.delete(0, tk.END)
            self.npc_personality.delete("1.0", tk.END)
            self.npc_ideals.delete("1.0", tk.END)
            self.npc_bonds.delete("1.0", tk.END)
            self.npc_flaws.delete("1.0", tk.END)
            self.npc_backstory.delete("1.0", tk.END)
            self.npc_role.delete(0, tk.END)
            self.npc_alignment.delete(0, tk.END)
            self.npc_deity.delete(0, tk.END)
            self.npc_faction.delete(0, tk.END)
            self.npc_faction.insert(0, "None")
            self.npc_image_path.delete(0, tk.END)
        except Exception as e:
            logger.error(f"Error clearing NPC form: {e}")
            messagebox.showerror("Error", f"Failed to clear NPC form: {e}")

    def populate_npc_listbox(self):
        """
        Populates the Listbox with existing NPCs.
        """
        try:
            records = self.db.get_npcs()
            self.npc_listbox.delete(0, tk.END)
            for record in records:
                display_text = f"{record[1]}"  # Display the name
                self.npc_listbox.insert(tk.END, display_text)
        except Exception as e:
            logger.error(f"Failed to populate NPC list: {e}")
            messagebox.showerror("Error", f"Failed to populate NPC list: {str(e)}")

    def display_selected_npc(self, event):
        """
        Displays the details of the selected NPC with Markdown rendering.
        """
        try:
            selection = self.npc_listbox.curselection()
            if selection:
                index = selection[0]
                records = self.db.get_npcs()
                selected_record = records[index]
                npc_details = self.format_npc_details(selected_record)
                # Convert Markdown to HTML
                html_content = markdown.markdown(npc_details, extensions=['fenced_code', 'tables'])
                # Update the HTMLLabel content
                self.npc_details_display.set_html(html_content)
        except Exception as e:
            logger.error(f"Failed to display selected NPC: {e}")
            messagebox.showerror("Error", f"Failed to display selected NPC: {str(e)}")

    def format_npc_details(self, record):
        """
        Formats NPC details for display in Markdown.

        Parameters:
            record (tuple): The NPC record fetched from the database.

        Returns:
            str: Formatted string of NPC details in Markdown.
        """
        fields = [
            "ID", "Name", "Race", "Class", "Gender", "Age", "Appearance",
            "Background", "Languages", "Personality Traits", "Ideals",
            "Bonds", "Flaws", "Backstory", "Role in World", "Alignment",
            "Deity", "Image Path", "Current Location", "Faction Affiliation",
            "Current Status", "Reputation", "Relationship to Party", "Last Seen",
            "Notes", "Possessions", "Secrets"
        ]
        npc_info = ""
        for i, field in enumerate(fields):
            value = record[i]
            if field == "Image Path" and value:
                # Embed image if path is provided
                if os.path.isfile(value):
                    # Convert path to URI format using pathlib
                    image_url = Path(value).absolute().as_uri()
                    npc_info += f"**{field}:** ![]({image_url})\n\n"
                else:
                    npc_info += f"**{field}:** {value}\n\n"
            else:
                npc_info += f"**{field}:** {value}\n\n"
        return npc_info

    # --- Maps Tab ---
    def create_maps_tab(self):
        """
        Sets up the Maps management interface.
        """
        try:
            # Frame for Map Upload and Metadata
            upload_frame = ttk.LabelFrame(self.maps_tab, text="Upload New Map")
            upload_frame.pack(padx=10, pady=10, fill='x')

            # Map Name
            ttk.Label(upload_frame, text="Name:").grid(row=0, column=0, sticky='w', pady=2)
            self.map_name_entry = ttk.Entry(upload_frame)
            self.map_name_entry.grid(row=0, column=1, sticky='ew', pady=2)

            # Upload Button
            upload_button = ttk.Button(upload_frame, text="Upload Map Image", command=self.upload_map)
            upload_button.grid(row=0, column=2, sticky='w', pady=2, padx=5)

            # Additional Metadata Fields
            metadata_fields = ["Campaign", "World", "Location", "Adventure", "Theme", "Description"]
            self.map_metadata_entries = {}
            for idx, field in enumerate(metadata_fields, start=1):
                ttk.Label(upload_frame, text=f"{field}:").grid(row=idx, column=0, sticky='w', pady=2)
                entry = ttk.Entry(upload_frame)
                entry.grid(row=idx, column=1, sticky='ew', pady=2)
                self.map_metadata_entries[field.lower()] = entry

            # Configure grid weights
            upload_frame.columnconfigure(1, weight=1)

            # Save Map Button
            save_map_button = ttk.Button(upload_frame, text="Save Map", command=self.save_map)
            save_map_button.grid(row=len(metadata_fields)+1, column=1, sticky='e', pady=10)

            # Separator
            separator = ttk.Separator(self.maps_tab, orient='horizontal')
            separator.pack(fill='x', padx=10, pady=5)

            # Frame for Map List and Display
            display_frame = ttk.Frame(self.maps_tab)
            display_frame.pack(padx=10, pady=10, fill='both', expand=True)

            # Listbox for Existing Maps
            listbox_frame = ttk.Frame(display_frame)
            listbox_frame.pack(side='left', fill='y', padx=(0, 10))

            ttk.Label(listbox_frame, text="Existing Maps:").pack(anchor='w')

            self.maps_listbox = tk.Listbox(listbox_frame)
            self.maps_listbox.pack(side='left', fill='y')
            self.maps_listbox.bind('<<ListboxSelect>>', self.display_selected_map)

            # Scrollbar for Listbox
            scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.maps_listbox.yview)
            scrollbar.pack(side='left', fill='y')
            self.maps_listbox.config(yscrollcommand=scrollbar.set)

            # Frame for Map Display and Controls
            map_display_frame = ttk.Frame(display_frame)
            map_display_frame.pack(side='left', fill='both', expand=True)

            # Canvas for Map Display with Scrollbars
            canvas_frame = ttk.Frame(map_display_frame)
            canvas_frame.pack(fill='both', expand=True)

            self.map_canvas = tk.Canvas(canvas_frame, bg='grey')
            self.map_canvas.pack(side='left', fill='both', expand=True)

            # Scrollbars
            self.h_scroll = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.map_canvas.xview)
            self.h_scroll.pack(side='bottom', fill='x')
            self.v_scroll = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.map_canvas.yview)
            self.v_scroll.pack(side='right', fill='y')

            self.map_canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

            # Bind resize event
            self.map_canvas.bind("<Configure>", self.resize_map_canvas)

            # Controls Frame
            controls_frame = ttk.Frame(map_display_frame)
            controls_frame.pack(fill='x', pady=5)

            # Grid Toggle
            self.grid_var = tk.BooleanVar()
            grid_checkbox = ttk.Checkbutton(controls_frame, text="Show 1/4\" Grid", variable=self.grid_var, command=self.toggle_grid)
            grid_checkbox.pack(side='left', padx=5)

            # Generate Dungeon Button
            generate_dungeon_button = ttk.Button(controls_frame, text="Generate Dungeon", command=self.generate_dungeon)
            generate_dungeon_button.pack(side='left', padx=5)

            # Drawing Tools Button
            drawing_tools_button = ttk.Button(controls_frame, text="Open Drawing Tools", command=self.open_drawing_tools)
            drawing_tools_button.pack(side='left', padx=5)

            # Load existing maps into the listbox
            self.populate_maps_listbox()
        except Exception as e:
            logger.error(f"Error creating Maps Tab: {e}")
            raise

    def upload_map(self):
        """
        Opens a file dialog to select an image to upload as a map.
        """
        try:
            file_path = filedialog.askopenfilename(
                title="Select Map Image",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg"), ("All Files", "*.*")]
            )
            if file_path:
                # Display the selected image path in the map name entry
                name = os.path.splitext(os.path.basename(file_path))[0]
                self.map_name_entry.delete(0, tk.END)
                self.map_name_entry.insert(0, name)
                # Store the image path temporarily for saving
                self.selected_map_image_path = file_path
                messagebox.showinfo("Image Selected", f"Selected image: {file_path}")
        except Exception as e:
            logger.error(f"Error uploading map: {e}")
            messagebox.showerror("Error", f"Failed to upload map: {e}")

    def save_map(self):
        """
        Saves the uploaded map and its metadata to the database.
        """
        try:
            name = self.map_name_entry.get().strip()
            if not name:
                messagebox.showwarning("Input Error", "Please provide a name for the map.")
                return

            # Get metadata
            campaign = self.map_metadata_entries['campaign'].get().strip()
            world = self.map_metadata_entries['world'].get().strip()
            location = self.map_metadata_entries['location'].get().strip()
            adventure = self.map_metadata_entries['adventure'].get().strip()
            theme = self.map_metadata_entries['theme'].get().strip()
            description = self.map_metadata_entries['description'].get().strip()

            # Get image data
            if hasattr(self, 'selected_map_image_path') and self.selected_map_image_path:
                with open(self.selected_map_image_path, 'rb') as file:
                    image_data = file.read()
            else:
                messagebox.showwarning("Input Error", "Please upload a map image before saving.")
                return

            # Save to database
            map_id = self.db.add_map(name, image_data, campaign, world, location, adventure, theme, description)
            messagebox.showinfo("Success", f"Map '{name}' saved successfully.")
            self.populate_maps_listbox()
            self.clear_map_form()
            # Add to FAISS index
            new_map = self.db.get_map_by_id(map_id)
            self.chat_manager.add_record_to_index('maps', new_map)
        except Exception as e:
            logger.error(f"Failed to save map: {e}")
            messagebox.showerror("Error", f"Failed to save map: {e}")

    def populate_maps_listbox(self):
        """
        Populates the Listbox with existing maps.
        """
        try:
            records = self.db.get_maps()
            self.maps_listbox.delete(0, tk.END)
            for record in records:
                display_text = f"{record[1]} ({record[3]})"  # Name (World)
                self.maps_listbox.insert(tk.END, display_text)
        except Exception as e:
            logger.error(f"Failed to populate maps list: {e}")
            messagebox.showerror("Error", f"Failed to populate maps list: {e}")

    def display_selected_map(self, event):
        """
        Displays the selected map image on the canvas with optional grid.
        """
        try:
            selection = self.maps_listbox.curselection()
            if selection:
                index = selection[0]
                records = self.db.get_maps()
                selected_record = records[index]
                map_id = selected_record[0]
                map_data = self.db.get_map_by_id(map_id)
                image_blob = map_data[2]

                # Load image from blob
                image = Image.open(io.BytesIO(image_blob))
                self.display_image_on_canvas(image)

                # Store current map ID for future reference (e.g., editing)
                self.current_map_id = map_id
        except Exception as e:
            logger.error(f"Failed to display selected map: {e}")
            messagebox.showerror("Error", f"Failed to display selected map: {e}")

    def display_image_on_canvas(self, image):
        """
        Displays a PIL image on the Tkinter Canvas with scrollbars.
        """
        try:
            self.map_canvas.delete("all")  # Clear previous image

            # Resize image if it's too large
            max_size = (2000, 2000)
            image.thumbnail(max_size, Image.ANTIALIAS)

            self.map_display_image = ImageTk.PhotoImage(image)
            self.map_canvas.create_image(0, 0, anchor='nw', image=self.map_display_image)
            self.map_canvas.config(scrollregion=self.map_canvas.bbox(tk.ALL))

            if self.grid_var.get():
                self.draw_grid(image.width, image.height)
        except Exception as e:
            logger.error(f"Error displaying image on canvas: {e}")
            messagebox.showerror("Error", f"Failed to display map image: {e}")

    def clear_map_form(self):
        """
        Clears the map upload form fields.
        """
        try:
            self.map_name_entry.delete(0, tk.END)
            for entry in self.map_metadata_entries.values():
                entry.delete(0, tk.END)
            if hasattr(self, 'selected_map_image_path'):
                del self.selected_map_image_path
        except Exception as e:
            logger.error(f"Error clearing map form: {e}")

    def toggle_grid(self):
        """
        Toggles the grid overlay on the map canvas.
        """
        try:
            selection = self.maps_listbox.curselection()
            if selection:
                index = selection[0]
                records = self.db.get_maps()
                selected_record = records[index]
                map_id = selected_record[0]
                map_data = self.db.get_map_by_id(map_id)
                image_blob = map_data[2]

                image = Image.open(io.BytesIO(image_blob))
                self.display_image_on_canvas(image)
        except Exception as e:
            logger.error(f"Error toggling grid: {e}")
            messagebox.showerror("Error", f"Failed to toggle grid: {e}")

    def draw_grid(self, width, height):
        """
        Draws a 1/4" grid on the canvas based on image dimensions.
        Assumes 96 DPI for screen display (1 inch = 96 pixels).
        """
        try:
            grid_size = 24  # 1/4" at 96 DPI
            for x in range(0, width, grid_size):
                self.map_canvas.create_line(x, 0, x, height, fill='black', width=1)
            for y in range(0, height, grid_size):
                self.map_canvas.create_line(0, y, width, y, fill='black', width=1)
        except Exception as e:
            logger.error(f"Error drawing grid: {e}")
            messagebox.showerror("Error", f"Failed to draw grid: {e}")

    def open_drawing_tools(self):
        """
        Opens a new window with basic drawing tools to create or edit a map.
        """
        try:
            drawing_window = tk.Toplevel(self.root)
            drawing_window.title("Map Drawing Tools")

            # Canvas for Drawing
            drawing_canvas = tk.Canvas(drawing_window, bg='white', width=800, height=600)
            drawing_canvas.pack(fill='both', expand=True)

            # Initialize PIL image to draw on
            self.drawing_image = Image.new("RGB", (800, 600), "white")
            self.draw = ImageDraw.Draw(self.drawing_image)

            # Current tool and color
            self.current_tool = tk.StringVar(value='pencil')
            self.current_color = '#000000'

            # Toolbar Frame
            toolbar = ttk.Frame(drawing_window)
            toolbar.pack(fill='x')

            # Tool Selection
            tools = ['pencil', 'line', 'rectangle', 'oval']
            for tool in tools:
                ttk.Radiobutton(toolbar, text=tool.capitalize(), variable=self.current_tool, value=tool).pack(side='left', padx=2)

            # Color Picker
            color_button = ttk.Button(toolbar, text="Select Color", command=self.select_color)
            color_button.pack(side='left', padx=5)

            # Save Button
            save_button = ttk.Button(toolbar, text="Save Drawing", command=lambda: self.save_drawing(drawing_window))
            save_button.pack(side='right', padx=5)

            # Bind mouse events
            drawing_canvas.bind("<ButtonPress-1>", self.start_draw)
            drawing_canvas.bind("<B1-Motion>", self.draw_motion)
            drawing_canvas.bind("<ButtonRelease-1>", self.end_draw)

            self.drawing_canvas_widget = drawing_canvas
            self.drawing_start_x = None
            self.drawing_start_y = None
            self.current_drawn_item = None
        except Exception as e:
            logger.error(f"Error opening drawing tools: {e}")
            messagebox.showerror("Error", f"Failed to open drawing tools: {e}")

    def select_color(self):
        """
        Opens a color chooser dialog to select drawing color.
        """
        try:
            color = colorchooser.askcolor()[1]
            if color:
                self.current_color = color
        except Exception as e:
            logger.error(f"Error selecting color: {e}")
            messagebox.showerror("Error", f"Failed to select color: {e}")

    def start_draw(self, event):
        """
        Initializes the drawing action.
        """
        try:
            self.drawing_start_x = event.x
            self.drawing_start_y = event.y
            if self.current_tool.get() == 'pencil':
                self.map_canvas.create_line(event.x, event.y, event.x+1, event.y+1, fill=self.current_color, width=2)
                self.draw.line([event.x, event.y, event.x+1, event.y+1], fill=self.current_color, width=2)
        except Exception as e:
            logger.error(f"Error starting draw: {e}")
            messagebox.showerror("Error", f"Failed to start drawing: {e}")

    def draw_motion(self, event):
        """
        Handles the drawing motion.
        """
        try:
            if self.current_tool.get() == 'pencil':
                self.map_canvas.create_line(self.drawing_start_x, self.drawing_start_y, event.x, event.y, fill=self.current_color, width=2)
                self.draw.line([self.drawing_start_x, self.drawing_start_y, event.x, event.y], fill=self.current_color, width=2)
                self.drawing_start_x = event.x
                self.drawing_start_y = event.y
            else:
                if self.current_drawn_item:
                    self.map_canvas.delete(self.current_drawn_item)
                if self.current_tool.get() == 'line':
                    self.current_drawn_item = self.map_canvas.create_line(self.drawing_start_x, self.drawing_start_y, event.x, event.y, fill=self.current_color, width=2)
                elif self.current_tool.get() == 'rectangle':
                    self.current_drawn_item = self.map_canvas.create_rectangle(self.drawing_start_x, self.drawing_start_y, event.x, event.y, outline=self.current_color, width=2)
                elif self.current_tool.get() == 'oval':
                    self.current_drawn_item = self.map_canvas.create_oval(self.drawing_start_x, self.drawing_start_y, event.x, event.y, outline=self.current_color, width=2)
        except Exception as e:
            logger.error(f"Error during draw motion: {e}")
            messagebox.showerror("Error", f"Failed during drawing: {e}")

    def end_draw(self, event):
        """
        Finalizes the drawing action.
        """
        try:
            if self.current_tool.get() in ['line', 'rectangle', 'oval']:
                # Draw on the PIL image
                if self.current_tool.get() == 'line':
                    self.draw.line([self.drawing_start_x, self.drawing_start_y, event.x, event.y], fill=self.current_color, width=2)
                elif self.current_tool.get() == 'rectangle':
                    self.draw.rectangle([self.drawing_start_x, self.drawing_start_y, event.x, event.y], outline=self.current_color, width=2)
                elif self.current_tool.get() == 'oval':
                    self.draw.ellipse([self.drawing_start_x, self.drawing_start_y, event.x, event.y], outline=self.current_color, width=2)
                self.current_drawn_item = None
        except Exception as e:
            logger.error(f"Error ending draw: {e}")
            messagebox.showerror("Error", f"Failed to end drawing: {e}")

    def save_drawing(self, window):
        """
        Saves the drawing to the database as a new map.
        """
        try:
            # Prompt for map name and metadata
            save_dialog = tk.Toplevel(window)
            save_dialog.title("Save Drawing")

            ttk.Label(save_dialog, text="Name:").grid(row=0, column=0, sticky='w', pady=2, padx=5)
            name_entry = ttk.Entry(save_dialog, width=50)
            name_entry.grid(row=0, column=1, pady=2, padx=5)

            # Additional Metadata Fields
            metadata_fields = ["Campaign", "World", "Location", "Adventure", "Theme", "Description"]
            metadata_entries = {}
            for idx, field in enumerate(metadata_fields, start=1):
                ttk.Label(save_dialog, text=f"{field}:").grid(row=idx, column=0, sticky='w', pady=2, padx=5)
                entry = ttk.Entry(save_dialog, width=50)
                entry.grid(row=idx, column=1, pady=2, padx=5)
                metadata_entries[field.lower()] = entry

            # Save Button
            save_button = ttk.Button(save_dialog, text="Save", command=lambda: self.save_drawing_to_db(name_entry, metadata_entries, save_dialog))
            save_button.grid(row=len(metadata_fields)+1, column=1, sticky='e', pady=10, padx=5)
        except Exception as e:
            logger.error(f"Error opening save dialog: {e}")
            messagebox.showerror("Error", f"Failed to open save dialog: {e}")

    def save_drawing_to_db(self, name_entry, metadata_entries, dialog):
        """
        Saves the drawing from the drawing window to the database.
        """
        try:
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Input Error", "Please provide a name for the map.")
                return

            # Get metadata
            campaign = metadata_entries['campaign'].get().strip()
            world = metadata_entries['world'].get().strip()
            location = metadata_entries['location'].get().strip()
            adventure = metadata_entries['adventure'].get().strip()
            theme = metadata_entries['theme'].get().strip()
            description = metadata_entries['description'].get().strip()

            # Convert PIL image to bytes
            img_byte_arr = io.BytesIO()
            self.drawing_image.save(img_byte_arr, format='PNG')
            image_data = img_byte_arr.getvalue()

            # Save to database
            map_id = self.db.add_map(name, image_data, campaign, world, location, adventure, theme, description)
            messagebox.showinfo("Success", f"Drawing '{name}' saved successfully.")
            dialog.destroy()
            self.populate_maps_listbox()
            # Add to FAISS index
            new_map = self.db.get_map_by_id(map_id)
            self.chat_manager.add_record_to_index('maps', new_map)
        except Exception as e:
            logger.error(f"Failed to save drawing: {e}")
            messagebox.showerror("Error", f"Failed to save drawing: {e}")

    def generate_dungeon(self):
        """
        Generates and renders a dungeon on the canvas.
        """
        try:
            # Create the dungeon generator and generate a dungeon with 1 level
            dungeon_generator = DungeonGenerator()
            dungeon = dungeon_generator.generate_dungeon(num_levels=1)  # Adjust levels if needed

            # Clear the canvas before rendering
            self.map_canvas.delete("all")

            # Draw the generated dungeon on the canvas
            self.render_dungeon(dungeon)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate dungeon: {e}")

    def resize_map_canvas(self, event):
        """
        Resizes the canvas scroll region based on the image size.
        """
        try:
            if self.map_display_image:
                self.map_canvas.config(scrollregion=self.map_canvas.bbox(tk.ALL))
        except Exception as e:
            logger.error(f"Error resizing map canvas: {e}")

    # --- Closing the Application ---
    def on_closing(self):
        """
        Handles the application closing event by closing the database connection and destroying the root window.
        """
        try:
            self.db.close()
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
        self.root.destroy()

    # --- Helper Methods ---
    def rebuild_faiss_index(self):
        """
        Rebuilds the FAISS index after significant changes like edits.
        """
        try:
            response = messagebox.askyesno("Rebuild FAISS Index", "Rebuilding the FAISS index may take some time. Do you want to proceed?")
            if response:
                self.chat_manager.build_faiss_index()
                messagebox.showinfo("Success", "FAISS index rebuilt successfully.")
        except Exception as e:
            logger.error(f"Failed to rebuild FAISS index: {e}")
            messagebox.showerror("Error", f"Failed to rebuild FAISS index: {e}")
