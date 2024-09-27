# session_notes_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkhtmlview import HTMLLabel
import markdown
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SessionNotesTab(ttk.Frame):
    def __init__(self, parent, db, chat_manager):
        super().__init__(parent)
        self.db = db
        self.chat_manager = chat_manager
        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.Frame(self)
        input_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(input_frame, text="Date:").grid(row=0, column=0, sticky='w', pady=2)
        self.session_date = ttk.Entry(input_frame)
        self.session_date.grid(row=0, column=1, sticky='ew', pady=2)
        self.session_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(input_frame, text="Notes (Markdown supported):").grid(row=1, column=0, sticky='nw', pady=2)
        self.session_notes_input = tk.Text(input_frame, height=5)
        self.session_notes_input.grid(row=1, column=1, sticky='ew', pady=2)

        input_frame.columnconfigure(1, weight=1)

        save_button = tk.Button(input_frame, text="Save Session Notes", command=self.save_session_notes)
        save_button.grid(row=2, column=1, sticky='e', pady=10)

        edit_button = tk.Button(input_frame, text="Edit Selected", command=self.edit_selected_session)
        edit_button.grid(row=2, column=0, sticky='w', pady=10)

        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)

        display_frame = ttk.Frame(self)
        display_frame.pack(padx=10, pady=10, fill='both', expand=True)

        ttk.Label(display_frame, text="Existing Session Notes:").pack(anchor='w')

        self.session_listbox = tk.Listbox(display_frame)
        self.session_listbox.pack(side='left', fill='y', padx=(0,10), pady=5)
        self.session_listbox.bind('<<ListboxSelect>>', self.display_selected_session)

        scrollbar = ttk.Scrollbar(display_frame, orient='vertical', command=self.session_listbox.yview)
        scrollbar.pack(side='left', fill='y')
        self.session_listbox.config(yscrollcommand=scrollbar.set)

        self.session_notes_display = HTMLLabel(display_frame, html="<h2>Session Notes</h2><hr>", background="white")
        self.session_notes_display.pack(side='left', fill='both', expand=True)

        self.populate_session_listbox()

    def save_session_notes(self):
        try:
            date = self.session_date.get()
            notes = self.session_notes_input.get("1.0", tk.END).strip()
            if not date or not notes:
                messagebox.showwarning("Input Error", "Please provide both date and notes.")
                return
            record_id = self.db.add_session_notes(date, notes)
            messagebox.showinfo("Success", "Session notes saved.")
            self.session_notes_input.delete("1.0", tk.END)
            new_record = self.db.get_record_by_id('session_notes', record_id)
            self.chat_manager.add_record_to_index('session_notes', new_record)
            self.populate_session_listbox()
        except Exception as e:
            logger.error(f"Failed to save session notes: {e}")
            messagebox.showerror("Error", f"Failed to save session notes: {str(e)}")

    def populate_session_listbox(self):
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
        try:
            selection = self.session_listbox.curselection()
            if selection:
                index = selection[0]
                records = self.db.get_session_notes()
                selected_record = records[index]
                notes = selected_record[2]
                html_content = markdown.markdown(notes, extensions=['fenced_code', 'tables'])
                self.session_notes_display.set_html(html_content)
        except Exception as e:
            logger.error(f"Failed to display selected session note: {e}")
            messagebox.showerror("Error", f"Failed to display selected session note: {str(e)}")

    def edit_selected_session(self):
        try:
            selection = self.session_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selection Error", "Please select a session notes entry to edit.")
                return
            index = selection[0]
            records = self.db.get_session_notes()
            selected_record = records[index]
            record_id, current_date, current_notes, _ = selected_record

            edit_dialog = tk.Toplevel(self)
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
                            self.chat_manager.rebuild_faiss_index()
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