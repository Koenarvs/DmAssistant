# world_building_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkhtmlview import HTMLLabel
import markdown
import logging

logger = logging.getLogger(__name__)

class WorldBuildingTab(ttk.Frame):
    def __init__(self, parent, db, chat_manager):
        super().__init__(parent)
        self.db = db
        self.chat_manager = chat_manager
        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.Frame(self)
        input_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(input_frame, text="Title:").grid(row=0, column=0, sticky='w', pady=2)
        self.world_title = ttk.Entry(input_frame)
        self.world_title.grid(row=0, column=1, sticky='ew', pady=2)

        ttk.Label(input_frame, text="Content (Markdown supported):").grid(row=1, column=0, sticky='nw', pady=2)
        self.world_content_input = tk.Text(input_frame, height=5)
        self.world_content_input.grid(row=1, column=1, sticky='ew', pady=2)

        input_frame.columnconfigure(1, weight=1)

        save_button = tk.Button(input_frame, text="Save World Building", command=self.save_world_building)
        save_button.grid(row=2, column=1, sticky='e', pady=10)

        edit_button = tk.Button(input_frame, text="Edit Selected", command=self.edit_selected_world)
        edit_button.grid(row=2, column=0, sticky='w', pady=10)

        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)

        display_frame = ttk.Frame(self)
        display_frame.pack(padx=10, pady=10, fill='both', expand=True)

        ttk.Label(display_frame, text="Existing World Building Entries:").pack(anchor='w')

        self.world_listbox = tk.Listbox(display_frame)
        self.world_listbox.pack(side='left', fill='y', padx=(0,10), pady=5)
        self.world_listbox.bind('<<ListboxSelect>>', self.display_selected_world)

        scrollbar = ttk.Scrollbar(display_frame, orient='vertical', command=self.world_listbox.yview)
        scrollbar.pack(side='left', fill='y')
        self.world_listbox.config(yscrollcommand=scrollbar.set)

        self.world_content_display = HTMLLabel(display_frame, html="<h2>World Building Content</h2><hr>", background="white")
        self.world_content_display.pack(side='left', fill='both', expand=True)

        self.populate_world_listbox()

    def save_world_building(self):
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
            new_record = self.db.get_record_by_id('world_building', record_id)
            self.chat_manager.add_record_to_index('world_building', new_record)
            self.populate_world_listbox()
        except Exception as e:
            logger.error(f"Failed to save world building information: {e}")
            messagebox.showerror("Error", f"Failed to save world building information: {str(e)}")

    def populate_world_listbox(self):
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
        try:
            selection = self.world_listbox.curselection()
            if selection:
                index = selection[0]
                records = self.db.get_world_building()
                selected_record = records[index]
                content = selected_record[2]
                html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
                self.world_content_display.set_html(html_content)
        except Exception as e:
            logger.error(f"Failed to display selected world building entry: {e}")
            messagebox.showerror("Error", f"Failed to display selected world building entry: {str(e)}")

    def edit_selected_world(self):
        try:
            selection = self.world_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selection Error", "Please select a world building entry to edit.")
                return
            index = selection[0]
            records = self.db.get_world_building()
            selected_record = records[index]
            record_id, current_title, current_content, _ = selected_record

            edit_dialog = tk.Toplevel(self)
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
                            self.chat_manager.rebuild_faiss_index()
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