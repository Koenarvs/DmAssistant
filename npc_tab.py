# npc_tab.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkhtmlview import HTMLLabel
import markdown
from npc_generator import generate_npc
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class NPCTab(ttk.Frame):
    def __init__(self, parent, db, chat_manager, factions):
        super().__init__(parent)
        self.db = db
        self.chat_manager = chat_manager
        self.factions = factions
        self.create_widgets()

    def create_widgets(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=10, pady=10, fill='x')

        fields = [
            ("Name", "npc_name"), ("Race", "npc_race"), ("Class", "npc_class"),
            ("Gender", "npc_gender"), ("Age", "npc_age"), ("Languages", "npc_languages"),
            ("Role in World", "npc_role"), ("Alignment", "npc_alignment"),
            ("Deity", "npc_deity"), ("Faction", "npc_faction")
        ]

        for i, (label, attr) in enumerate(fields):
            ttk.Label(form_frame, text=f"{label}:").grid(row=i, column=0, sticky='w', pady=2)
            setattr(self, attr, ttk.Entry(form_frame))
            getattr(self, attr).grid(row=i, column=1, sticky='ew', pady=2)

        text_fields = [
            ("Appearance", "npc_appearance"), ("Background", "npc_background"),
            ("Personality Traits", "npc_personality"), ("Ideals", "npc_ideals"),
            ("Bonds", "npc_bonds"), ("Flaws", "npc_flaws"), ("Backstory", "npc_backstory")
        ]

        for i, (label, attr) in enumerate(text_fields, start=len(fields)):
            ttk.Label(form_frame, text=f"{label} (Markdown supported):").grid(row=i, column=0, sticky='nw', pady=2)
            setattr(self, attr, tk.Text(form_frame, height=3))
            getattr(self, attr).grid(row=i, column=1, sticky='ew', pady=2)

        ttk.Label(form_frame, text="Image Path:").grid(row=len(fields)+len(text_fields), column=0, sticky='w', pady=2)
        self.npc_image_path = ttk.Entry(form_frame)
        self.npc_image_path.grid(row=len(fields)+len(text_fields), column=1, sticky='ew', pady=2)
        browse_button = ttk.Button(form_frame, text="Browse", command=self.browse_image)
        browse_button.grid(row=len(fields)+len(text_fields), column=2, sticky='w', pady=2, padx=5)

        form_frame.columnconfigure(1, weight=1)

        create_npc_button = tk.Button(form_frame, text="Create NPC", command=self.create_npc)
        create_npc_button.grid(row=len(fields)+len(text_fields)+1, column=0, sticky='w', pady=10)

        save_npc_button = tk.Button(form_frame, text="Add NPC", command=self.add_npc)
        save_npc_button.grid(row=len(fields)+len(text_fields)+1, column=1, sticky='e', pady=10)

        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)

        list_frame = ttk.Frame(self)
        list_frame.pack(padx=10, pady=10, fill='both', expand=True)

        ttk.Label(list_frame, text="Existing NPCs:").pack(anchor='w')

        self.npc_listbox = tk.Listbox(list_frame)
        self.npc_listbox.pack(side='left', fill='y', padx=(0,10), pady=5)
        self.npc_listbox.bind('<<ListboxSelect>>', self.display_selected_npc)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.npc_listbox.yview)
        scrollbar.pack(side='left', fill='y')
        self.npc_listbox.config(yscrollcommand=scrollbar.set)

        self.npc_details_display = HTMLLabel(list_frame, html="<h2>NPC Details</h2><hr>", background="white")
        self.npc_details_display.pack(side='left', fill='both', expand=True)

        self.populate_npc_listbox()

    def create_npc(self):
        try:
            npc = generate_npc()

            for attr in ['name', 'race', 'class', 'gender', 'age', 'languages', 'role_in_world', 'alignment', 'deity']:
                getattr(self, f'npc_{attr}').delete(0, tk.END)
                getattr(self, f'npc_{attr}').insert(0, str(npc.get(attr, '')))

            for attr in ['appearance', 'background', 'personality_traits', 'ideals', 'bonds', 'flaws', 'backstory']:
                getattr(self, f'npc_{attr}').delete("1.0", tk.END)
                getattr(self, f'npc_{attr}').insert(tk.END, npc.get(attr, ''))

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
            }

            if not npc_data['name']:
                messagebox.showwarning("Input Error", "Please provide the NPC's name.")
                return

            if npc_data['age'] is None:
                messagebox.showwarning("Input Error", "Age must be a number.")
                return

            npc_id = self.db.add_npc(npc_data)
            messagebox.showinfo("Success", f"NPC '{npc_data['name']}' added successfully.")
            self.clear_npc_form()
            new_npc = self.db.get_npc_by_id(npc_id)
            self.chat_manager.add_record_to_index('npc', new_npc)
            self.populate_npc_listbox()
        except Exception as e:
            logger.error(f"Failed to add NPC: {e}")
            messagebox.showerror("Error", f"Failed to add NPC: {str(e)}")

    def clear_npc_form(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)

    def populate_npc_listbox(self):
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
        try:
            selection = self.npc_listbox.curselection()
            if selection:
                index = selection[0]
                records = self.db.get_npcs()
                selected_record = records[index]
                npc_details = self.format_npc_details(selected_record)
                html_content = markdown.markdown(npc_details, extensions=['fenced_code', 'tables'])
                self.npc_details_display.set_html(html_content)
        except Exception as e:
            logger.error(f"Failed to display selected NPC: {e}")
            messagebox.showerror("Error", f"Failed to display selected NPC: {str(e)}")

    def format_npc_details(self, record):
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
                if os.path.isfile(value):
                    image_url = Path(value).absolute().as_uri()
                    npc_info += f"**{field}:** ![]({image_url})\n\n"
                else:
                    npc_info += f"**{field}:** {value}\n\n"
            else:
                npc_info += f"**{field}:** {value}\n\n"
        return npc_info