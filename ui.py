# ui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from chat import ChatManager
from db import Database
from datetime import datetime

class DnDManagerApp:
    """
    The main user interface for the D&D Manager application.
    It includes tabs for ChatGPT interactions, World Building, Session Notes, and NPC Management.
    """
    def __init__(self, root, db):
        """
        Initializes the application with the root Tkinter window and the database connection.
        """
        self.root = root
        self.root.title("D&D Manager with ChatGPT and FAISS")
        self.db = db
        self.chat_manager = ChatManager(self.db)
        self.create_widgets()

    def create_widgets(self):
        """
        Creates the main tabbed interface and initializes each tab.
        """
        tab_control = ttk.Notebook(self.root)

        # Chat Tab
        self.chat_tab = ttk.Frame(tab_control)
        tab_control.add(self.chat_tab, text='ChatGPT')

        # World Building Tab
        self.world_tab = ttk.Frame(tab_control)
        tab_control.add(self.world_tab, text='World Building')

        # Session Notes Tab
        self.session_tab = ttk.Frame(tab_control)
        tab_control.add(self.session_tab, text='Session Notes')

        # NPC Management Tab
        self.npc_tab = ttk.Frame(tab_control)
        tab_control.add(self.npc_tab, text='NPC Management')

        tab_control.pack(expand=1, fill='both')

        self.create_chat_tab()
        self.create_world_tab()
        self.create_session_tab()
        self.create_npc_tab()

    # --- Chat Tab ---
    def create_chat_tab(self):
        """
        Sets up the ChatGPT interaction interface.
        """
        # Chat History
        self.chat_history = scrolledtext.ScrolledText(self.chat_tab, state='disabled', wrap='word')
        self.chat_history.pack(padx=10, pady=10, fill='both', expand=True)

        # Entry Field
        self.chat_entry = tk.Entry(self.chat_tab)
        self.chat_entry.pack(padx=10, pady=(0,10), fill='x')
        self.chat_entry.bind("<Return>", self.send_chat)

        # Send Button
        send_button = tk.Button(self.chat_tab, text="Send", command=self.send_chat)
        send_button.pack(padx=10, pady=(0,10))

    def send_chat(self, event=None):
        """
        Handles sending user input to ChatGPT and displaying the response.
        """
        user_input = self.chat_entry.get()
        if not user_input.strip():
            return
        self.chat_entry.delete(0, tk.END)
        self.update_chat_history("You", user_input)
        
        # Generate response with context using FAISS
        response = self.chat_manager.generate_response(user_input)
        self.update_chat_history("ChatGPT", response)

    def update_chat_history(self, sender, message):
        """
        Updates the chat history display with new messages.
        """
        self.chat_history.configure(state='normal')
        self.chat_history.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_history.configure(state='disabled')
        self.chat_history.see(tk.END)

    # --- World Building Tab ---
    def create_world_tab(self):
        """
        Sets up the World Building management interface.
        """
        # Title Entry
        tk.Label(self.world_tab, text="Title:").pack(padx=10, pady=(10,0), anchor='w')
        self.world_title = tk.Entry(self.world_tab)
        self.world_title.pack(padx=10, pady=(0,10), fill='x')

        # Content Text
        tk.Label(self.world_tab, text="Content:").pack(padx=10, pady=(10,0), anchor='w')
        self.world_content = scrolledtext.ScrolledText(self.world_tab, height=10)
        self.world_content.pack(padx=10, pady=(0,10), fill='both', expand=True)

        # Save Button
        save_button = tk.Button(self.world_tab, text="Save World Building", command=self.save_world_building)
        save_button.pack(padx=10, pady=(0,10))

        # Display Existing Entries
        self.display_world_building()

    def save_world_building(self):
        """
        Saves a new world building entry to the database and updates the FAISS index.
        """
        title = self.world_title.get()
        content = self.world_content.get("1.0", tk.END).strip()
        if not title or not content:
            messagebox.showwarning("Input Error", "Please provide both title and content.")
            return
        try:
            record_id = self.db.add_world_building(title, content)
            messagebox.showinfo("Success", "World building information saved.")
            self.world_title.delete(0, tk.END)
            self.world_content.delete("1.0", tk.END)
            # Add the new record to FAISS index incrementally
            new_record = self.db.get_record_by_id('world_building', record_id)
            self.chat_manager.add_record_to_index('world_building', new_record)
            self.display_world_building()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save world building information: {str(e)}")

    def display_world_building(self):
        """
        Displays all existing world building entries in the UI.
        """
        try:
            records = self.db.get_world_building()
            # Clear and update the ScrolledText widget
            self.world_content.configure(state='normal')
            self.world_content.delete("1.0", tk.END)
            display_text = ""
            for record in records:
                display_text += f"ID: {record[0]}\nTitle: {record[1]}\nContent: {record[2]}\n\n"
            self.world_content.insert(tk.END, display_text)
            self.world_content.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display world building information: {str(e)}")

    # --- Session Notes Tab ---
    def create_session_tab(self):
        """
        Sets up the Session Notes management interface.
        """
        # Date Entry
        tk.Label(self.session_tab, text="Date:").pack(padx=10, pady=(10,0), anchor='w')
        self.session_date = tk.Entry(self.session_tab)
        self.session_date.pack(padx=10, pady=(0,10), fill='x')
        self.session_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Notes Text
        tk.Label(self.session_tab, text="Notes:").pack(padx=10, pady=(10,0), anchor='w')
        self.session_notes = scrolledtext.ScrolledText(self.session_tab, height=10)
        self.session_notes.pack(padx=10, pady=(0,10), fill='both', expand=True)

        # Save Button
        save_button = tk.Button(self.session_tab, text="Save Session Notes", command=self.save_session_notes)
        save_button.pack(padx=10, pady=(0,10))

        # Display Existing Entries
        self.display_session_notes()

    def save_session_notes(self):
        """
        Saves new session notes to the database and updates the FAISS index.
        """
        date = self.session_date.get()
        notes = self.session_notes.get("1.0", tk.END).strip()
        if not date or not notes:
            messagebox.showwarning("Input Error", "Please provide both date and notes.")
            return
        try:
            record_id = self.db.add_session_notes(date, notes)
            messagebox.showinfo("Success", "Session notes saved.")
            self.session_notes.delete("1.0", tk.END)
            # Add the new record to FAISS index incrementally
            new_record = self.db.get_record_by_id('session_notes', record_id)
            self.chat_manager.add_record_to_index('session_notes', new_record)
            self.display_session_notes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session notes: {str(e)}")

    def display_session_notes(self):
        """
        Displays all existing session notes entries in the UI.
        """
        try:
            records = self.db.get_session_notes()
            # Clear and update the ScrolledText widget
            self.session_notes.configure(state='normal')
            self.session_notes.delete("1.0", tk.END)
            display_text = ""
            for record in records:
                display_text += f"ID: {record[0]}\nDate: {record[1]}\nNotes: {record[2]}\n\n"
            self.session_notes.insert(tk.END, display_text)
            self.session_notes.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display session notes: {str(e)}")

    # --- NPC Management Tab ---
    def create_npc_tab(self):
        """
        Sets up the NPC Management interface, including forms to add, edit, delete, and display NPCs.
        """
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
        ttk.Label(form_frame, text="Appearance:").grid(row=5, column=0, sticky='nw', pady=2)
        self.npc_appearance = scrolledtext.ScrolledText(form_frame, height=3)
        self.npc_appearance.grid(row=5, column=1, sticky='ew', pady=2)

        # Background
        ttk.Label(form_frame, text="Background:").grid(row=6, column=0, sticky='nw', pady=2)
        self.npc_background = scrolledtext.ScrolledText(form_frame, height=3)
        self.npc_background.grid(row=6, column=1, sticky='ew', pady=2)

        # Languages
        ttk.Label(form_frame, text="Languages:").grid(row=7, column=0, sticky='w', pady=2)
        self.npc_languages = ttk.Entry(form_frame)
        self.npc_languages.grid(row=7, column=1, sticky='ew', pady=2)

        # Personality Traits
        ttk.Label(form_frame, text="Personality Traits:").grid(row=8, column=0, sticky='nw', pady=2)
        self.npc_personality = scrolledtext.ScrolledText(form_frame, height=3)
        self.npc_personality.grid(row=8, column=1, sticky='ew', pady=2)

        # Ideals
        ttk.Label(form_frame, text="Ideals:").grid(row=9, column=0, sticky='nw', pady=2)
        self.npc_ideals = scrolledtext.ScrolledText(form_frame, height=3)
        self.npc_ideals.grid(row=9, column=1, sticky='ew', pady=2)

        # Bonds
        ttk.Label(form_frame, text="Bonds:").grid(row=10, column=0, sticky='nw', pady=2)
        self.npc_bonds = scrolledtext.ScrolledText(form_frame, height=3)
        self.npc_bonds.grid(row=10, column=1, sticky='ew', pady=2)

        # Flaws
        ttk.Label(form_frame, text="Flaws:").grid(row=11, column=0, sticky='nw', pady=2)
        self.npc_flaws = scrolledtext.ScrolledText(form_frame, height=3)
        self.npc_flaws.grid(row=11, column=1, sticky='ew', pady=2)

        # Backstory
        ttk.Label(form_frame, text="Backstory:").grid(row=12, column=0, sticky='nw', pady=2)
        self.npc_backstory = scrolledtext.ScrolledText(form_frame, height=3)
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

        # Image Path
        ttk.Label(form_frame, text="Image Path:").grid(row=16, column=0, sticky='w', pady=2)
        self.npc_image_path = ttk.Entry(form_frame)
        self.npc_image_path.grid(row=16, column=1, sticky='ew', pady=2)
        browse_button = ttk.Button(form_frame, text="Browse", command=self.browse_image)
        browse_button.grid(row=16, column=2, sticky='w', pady=2, padx=5)

        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)

        # Save NPC Button
        save_npc_button = tk.Button(form_frame, text="Add NPC", command=self.add_npc)
        save_npc_button.grid(row=17, column=1, sticky='e', pady=10)

        # Frame for NPC List
        list_frame = ttk.Frame(self.npc_tab)
        list_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # NPC List
        self.npc_list = scrolledtext.ScrolledText(list_frame, state='disabled', wrap='word')
        self.npc_list.pack(fill='both', expand=True)

        # Display Existing NPCs
        self.display_npcs()

    def browse_image(self):
        """
        Opens a file dialog to select an image for the NPC.
        """
        file_path = filedialog.askopenfilename(
            title="Select NPC Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif"), ("All Files", "*.*")]
        )
        if file_path:
            self.npc_image_path.delete(0, tk.END)
            self.npc_image_path.insert(0, file_path)

    def add_npc(self):
        """
        Collects NPC data from the form and adds it to the database.
        """
        npc_data = {
            'name': self.npc_name.get(),
            'race': self.npc_race.get(),
            'class': self.npc_class.get(),
            'gender': self.npc_gender.get(),
            'age': self.npc_age.get(),
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
            'image_path': self.npc_image_path.get(),
            # Dynamic Information can be added here as needed
        }

        # Basic validation
        if not npc_data['name']:
            messagebox.showwarning("Input Error", "Please provide the NPC's name.")
            return

        try:
            npc_id = self.db.add_npc(npc_data)
            messagebox.showinfo("Success", f"NPC '{npc_data['name']}' added successfully.")
            self.clear_npc_form()
            # Add the new NPC to FAISS index incrementally
            new_npc = self.db.get_npc_by_id(npc_id)
            self.chat_manager.add_record_to_index('npc', new_npc)
            self.display_npcs()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add NPC: {str(e)}")

    def clear_npc_form(self):
        """
        Clears all input fields in the NPC form.
        """
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
        self.npc_image_path.delete(0, tk.END)

    def display_npcs(self):
        """
        Displays all existing NPCs in the NPC list area.
        """
        try:
            records = self.db.get_npcs()
            self.npc_list.configure(state='normal')
            self.npc_list.delete("1.0", tk.END)
            for record in records:
                npc_info = f"ID: {record[0]}\nName: {record[1]}\nRace: {record[2]}\nClass: {record[3]}\nGender: {record[4]}\nAge: {record[5]}\nAppearance: {record[6]}\nBackground: {record[7]}\nLanguages: {record[8]}\nPersonality Traits: {record[9]}\nIdeals: {record[10]}\nBonds: {record[11]}\nFlaws: {record[12]}\nBackstory: {record[13]}\nRole in World: {record[14]}\nAlignment: {record[15]}\nDeity: {record[16]}\nCurrent Location: {record[17]}\nFaction Affiliation: {record[18]}\nCurrent Status: {record[19]}\nReputation: {record[20]}\nRelationship to Party: {record[21]}\nLast Seen: {record[22]}\nNotes: {record[23]}\nPossessions: {record[24]}\nSecrets: {record[25]}\n\n"
                self.npc_list.insert(tk.END, npc_info)
            self.npc_list.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display NPCs: {str(e)}")

    # --- Additional NPC Management Features ---
    # Future enhancements can include editing and deleting NPCs through the UI

    def on_closing(self):
        """
        Handles the application closing event by closing the database connection and destroying the root window.
        """
        self.db.close()
        self.root.destroy()
