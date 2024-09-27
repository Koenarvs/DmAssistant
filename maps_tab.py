# maps_tab.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from PIL import Image, ImageTk, ImageDraw
import io
import os
import logging
from dungeon_generator import DungeonGenerator

logger = logging.getLogger(__name__)

class MapsTab(ttk.Frame):
    def __init__(self, parent, db, chat_manager):
        super().__init__(parent)
        self.db = db
        self.chat_manager = chat_manager
        self.create_widgets()

    def create_widgets(self):
        upload_frame = ttk.LabelFrame(self, text="Upload New Map")
        upload_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(upload_frame, text="Name:").grid(row=0, column=0, sticky='w', pady=2)
        self.map_name_entry = ttk.Entry(upload_frame)
        self.map_name_entry.grid(row=0, column=1, sticky='ew', pady=2)

        upload_button = ttk.Button(upload_frame, text="Upload Map Image", command=self.upload_map)
        upload_button.grid(row=0, column=2, sticky='w', pady=2, padx=5)

        metadata_fields = ["Campaign", "World", "Location", "Adventure", "Theme", "Description"]
        self.map_metadata_entries = {}
        for idx, field in enumerate(metadata_fields, start=1):
            ttk.Label(upload_frame, text=f"{field}:").grid(row=idx, column=0, sticky='w', pady=2)
            entry = ttk.Entry(upload_frame)
            entry.grid(row=idx, column=1, sticky='ew', pady=2)
            self.map_metadata_entries[field.lower()] = entry

        upload_frame.columnconfigure(1, weight=1)

        save_map_button = ttk.Button(upload_frame, text="Save Map", command=self.save_map)
        save_map_button.grid(row=len(metadata_fields)+1, column=1, sticky='e', pady=10)

        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)

        display_frame = ttk.Frame(self)
        display_frame.pack(padx=10, pady=10, fill='both', expand=True)

        listbox_frame = ttk.Frame(display_frame)
        listbox_frame.pack(side='left', fill='y', padx=(0,10))

        ttk.Label(listbox_frame, text="Existing Maps:").pack(anchor='w')

        self.maps_listbox = tk.Listbox(listbox_frame)
        self.maps_listbox.pack(side='left', fill='y')
        self.maps_listbox.bind('<<ListboxSelect>>', self.display_selected_map)

        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.maps_listbox.yview)
        scrollbar.pack(side='left', fill='y')
        self.maps_listbox.config(yscrollcommand=scrollbar.set)

        map_display_frame = ttk.Frame(display_frame)
        map_display_frame.pack(side='left', fill='both', expand=True)

        canvas_frame = ttk.Frame(map_display_frame)
        canvas_frame.pack(fill='both', expand=True)

        self.map_canvas = tk.Canvas(canvas_frame, bg='grey', width=800, height=600)
        self.map_canvas.pack(side='left', fill='both', expand=True)

        self.h_scroll = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.map_canvas.xview)
        self.h_scroll.pack(side='bottom', fill='x')
        self.v_scroll = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.map_canvas.yview)
        self.v_scroll.pack(side='right', fill='y')

        self.map_canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.map_canvas.bind("<Configure>", self.resize_map_canvas)

        controls_frame = ttk.Frame(map_display_frame)
        controls_frame.pack(fill='x', pady=5)

        self.grid_var = tk.BooleanVar()
        grid_checkbox = ttk.Checkbutton(controls_frame, text="Show 1/4\" Grid", variable=self.grid_var, command=self.toggle_grid)
        grid_checkbox.pack(side='left', padx=5)

        generate_dungeon_button = ttk.Button(controls_frame, text="Generate Dungeon", command=self.generate_dungeon)
        generate_dungeon_button.pack(side='left', padx=5)

        drawing_tools_button = ttk.Button(controls_frame, text="Open Drawing Tools", command=self.open_drawing_tools)
        drawing_tools_button.pack(side='left', padx=5)

        edit_button = ttk.Button(controls_frame, text="Edit Map", command=self.edit_map)
        edit_button.pack(side='left', padx=5)

        delete_button = ttk.Button(controls_frame, text="Delete Map", command=self.delete_map)
        delete_button.pack(side='left', padx=5)

        self.populate_maps_listbox()

    def upload_map(self):
        try:
            file_path = filedialog.askopenfilename(
                title="Select Map Image",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg"), ("All Files", "*.*")]
            )
            if file_path:
                name = os.path.splitext(os.path.basename(file_path))[0]
                self.map_name_entry.delete(0, tk.END)
                self.map_name_entry.insert(0, name)
                self.selected_map_image_path = file_path
                messagebox.showinfo("Image Selected", f"Selected image: {file_path}")
        except Exception as e:
            logger.error(f"Error uploading map: {e}")
            messagebox.showerror("Error", f"Failed to upload map: {e}")

    def save_map(self):
        try:
            name = self.map_name_entry.get().strip()
            if not name:
                messagebox.showwarning("Input Error", "Please provide a name for the map.")
                return

            campaign = self.map_metadata_entries['campaign'].get().strip()
            world = self.map_metadata_entries['world'].get().strip()
            location = self.map_metadata_entries['location'].get().strip()
            adventure = self.map_metadata_entries['adventure'].get().strip()
            theme = self.map_metadata_entries['theme'].get().strip()
            description = self.map_metadata_entries['description'].get().strip()

            if hasattr(self, 'selected_map_image_path') and self.selected_map_image_path:
                with open(self.selected_map_image_path, 'rb') as file:
                    image_data = file.read()
            else:
                messagebox.showwarning("Input Error", "Please upload a map image before saving.")
                return

            map_id = self.db.add_map(name, image_data, campaign, world, location, adventure, theme, description)
            messagebox.showinfo("Success", f"Map '{name}' saved successfully.")
            self.populate_maps_listbox()
            self.clear_map_form()
            new_map = self.db.get_map_by_id(map_id)
            self.chat_manager.add_record_to_index('maps', new_map)
        except Exception as e:
            logger.error(f"Failed to save map: {e}")
            messagebox.showerror("Error", f"Failed to save map: {e}")

    def populate_maps_listbox(self):
        try:
            records = self.db.get_maps()
            self.maps_listbox.delete(0, tk.END)
            for record in records:
                display_text = f"{record['name']} ({record['world']})"  # Name (World)
                self.maps_listbox.insert(tk.END, display_text)
        except Exception as e:
            logger.error(f"Failed to populate maps list: {e}")
            messagebox.showerror("Error", f"Failed to populate maps list: {e}")

    def display_selected_map(self, event):
        try:
            selection = self.maps_listbox.curselection()
            if selection:
                index = selection[0]
                records = self.db.get_maps()
                selected_record = records[index]
                map_id = selected_record['id']
                map_data = self.db.get_map_by_id(map_id)
                image_blob = map_data['image']

                image = Image.open(io.BytesIO(image_blob))
                self.display_image_on_canvas(image)

                self.current_map_id = map_id
        except Exception as e:
            logger.error(f"Failed to display selected map: {e}")
            messagebox.showerror("Error", f"Failed to display selected map: {e}")

    def display_image_on_canvas(self, image):
        try:
            self.map_canvas.delete("all")

            max_size = (2000, 2000)
            image.thumbnail(max_size, Image.LANCZOS)

            self.map_display_image = ImageTk.PhotoImage(image)
            self.map_canvas.create_image(0, 0, anchor='nw', image=self.map_display_image)
            self.map_canvas.config(scrollregion=self.map_canvas.bbox(tk.ALL))

            if self.grid_var.get():
                self.draw_grid(image.width, image.height)
        except Exception as e:
            logger.error(f"Error displaying image on canvas: {e}")
            messagebox.showerror("Error", f"Failed to display map image: {e}")

    def clear_map_form(self):
        self.map_name_entry.delete(0, tk.END)
        for entry in self.map_metadata_entries.values():
            entry.delete(0, tk.END)
        if hasattr(self, 'selected_map_image_path'):
            del self.selected_map_image_path

    def toggle_grid(self):
        try:
            selection = self.maps_listbox.curselection()
            if selection:
                index = selection[0]
                records = self.db.get_maps()
                selected_record = records[index]
                map_id = selected_record['id']
                map_data = self.db.get_map_by_id(map_id)
                image_blob = map_data['image']

                image = Image.open(io.BytesIO(image_blob))
                self.display_image_on_canvas(image)
        except Exception as e:
            logger.error(f"Error toggling grid: {e}")
            messagebox.showerror("Error", f"Failed to toggle grid: {e}")

    def draw_grid(self, width, height):
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
        try:
            drawing_window = tk.Toplevel(self)
            drawing_window.title("Map Drawing Tools")

            drawing_canvas = tk.Canvas(drawing_window, bg='white', width=800, height=600)
            drawing_canvas.pack(fill='both', expand=True)

            self.drawing_image = Image.new("RGB", (800, 600), "white")
            self.draw = ImageDraw.Draw(self.drawing_image)

            self.current_tool = tk.StringVar(value='pencil')
            self.current_color = '#000000'

            toolbar = ttk.Frame(drawing_window)
            toolbar.pack(fill='x')

            tools = ['pencil', 'line', 'rectangle', 'oval']
            for tool in tools:
                ttk.Radiobutton(toolbar, text=tool.capitalize(), variable=self.current_tool, value=tool).pack(side='left', padx=2)

            color_button = ttk.Button(toolbar, text="Select Color", command=self.select_color)
            color_button.pack(side='left', padx=5)

            save_button = ttk.Button(toolbar, text="Save Drawing", command=lambda: self.save_drawing(drawing_window))
            save_button.pack(side='right', padx=5)

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
        try:
            color = colorchooser.askcolor()[1]
            if color:
                self.current_color = color
        except Exception as e:
            logger.error(f"Error selecting color: {e}")
            messagebox.showerror("Error", f"Failed to select color: {e}")

    def start_draw(self, event):
        try:
            self.drawing_start_x = event.x
            self.drawing_start_y = event.y
            if self.current_tool.get() == 'pencil':
                self.drawing_canvas_widget.create_line(event.x, event.y, event.x+1, event.y+1, fill=self.current_color, width=2)
                self.draw.line([event.x, event.y, event.x+1, event.y+1], fill=self.current_color, width=2)
        except Exception as e:
            logger.error(f"Error starting draw: {e}")
            messagebox.showerror("Error", f"Failed to start drawing: {e}")

    def draw_motion(self, event):
        try:
            if self.current_tool.get() == 'pencil':
                self.drawing_canvas_widget.create_line(self.drawing_start_x, self.drawing_start_y, event.x, event.y, fill=self.current_color, width=2)
                self.draw.line([self.drawing_start_x, self.drawing_start_y, event.x, event.y], fill=self.current_color, width=2)
                self.drawing_start_x = event.x
                self.drawing_start_y = event.y
            else:
                if self.current_drawn_item:
                    self.drawing_canvas_widget.delete(self.current_drawn_item)
                if self.current_tool.get() == 'line':
                    self.current_drawn_item = self.drawing_canvas_widget.create_line(self.drawing_start_x, self.drawing_start_y, event.x, event.y, fill=self.current_color, width=2)
                elif self.current_tool.get() == 'rectangle':
                    self.current_drawn_item = self.drawing_canvas_widget.create_rectangle(self.drawing_start_x, self.drawing_start_y, event.x, event.y, outline=self.current_color, width=2)
                elif self.current_tool.get() == 'oval':
                    self.current_drawn_item = self.drawing_canvas_widget.create_oval(self.drawing_start_x, self.drawing_start_y, event.x, event.y, outline=self.current_color, width=2)
        except Exception as e:
            logger.error(f"Error during draw motion: {e}")
            messagebox.showerror("Error", f"Failed during drawing: {e}")

    def end_draw(self, event):
        try:
            if self.current_tool.get() in ['line', 'rectangle', 'oval']:
                x0, y0 = min(self.drawing_start_x, event.x), min(self.drawing_start_y, event.y)
                x1, y1 = max(self.drawing_start_x, event.x), max(self.drawing_start_y, event.y)
                if self.current_tool.get() == 'line':
                    self.draw.line([x0, y0, x1, y1], fill=self.current_color, width=2)
                elif self.current_tool.get() == 'rectangle':
                    self.draw.rectangle([x0, y0, x1, y1], outline=self.current_color, width=2)
                elif self.current_tool.get() == 'oval':
                    self.draw.ellipse([x0, y0, x1, y1], outline=self.current_color, width=2)
                self.current_drawn_item = None
        except Exception as e:
            logger.error(f"Error ending draw: {e}")
            messagebox.showerror("Error", f"Failed to end drawing: {e}")

    def resize_map_canvas(self, event):
        try:
            if hasattr(self, 'map_display_image'):
                self.map_canvas.config(scrollregion=self.map_canvas.bbox(tk.ALL))
        except Exception as e:
            logger.error(f"Error resizing map canvas: {e}")
            messagebox.showerror("Error", f"Failed to resize map canvas: {e}")

    def generate_dungeon(self):
        """
        Generates and renders a dungeon on the canvas.
        """
        try:
            # Create the dungeon generator and generate a dungeon with 3 levels
            dungeon_generator = DungeonGenerator()
            dungeon_generator.generate_dungeon(num_levels=1)  # You can adjust the number of levels here

            # Clear the canvas
            self.map_canvas.delete("all")

            # Draw the dungeon on the canvas
            self.render_dungeon(dungeon_generator.dungeon)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate dungeon: {e}")

    def render_dungeon(self, dungeon):
        """
        Renders the dungeon on the canvas.
        """
        try:
            room_size = 50  # Size of each room on the canvas
            padding = 10  # Space between rooms

            for level_idx, level in enumerate(dungeon.levels):
                for room_idx, room in enumerate(level.rooms):
                    x = padding + (room_idx * (room_size + padding))  # Adjust the X position
                    y = padding + (level_idx * (room_size + padding * 3))  # Adjust the Y position based on level
                    
                    # Draw the room as a rectangle
                    self.map_canvas.create_rectangle(x, y, x + room_size, y + room_size, fill="white", outline="black")
                    
                    # Add room number inside the room
                    self.map_canvas.create_text(x + room_size / 2, y + room_size / 2, text=str(room_idx + 1))

                    # Draw connections to connected rooms
                    for connected_room in room.connections:
                        # Calculate the position of the connected room
                        connected_idx = level.rooms.index(connected_room)
                        connected_x = padding + (connected_idx * (room_size + padding))
                        connected_y = y  # Same Y position since it's in the same level

                        # Draw a line to the connected room
                        self.map_canvas.create_line(x + room_size / 2, y + room_size / 2,
                                                    connected_x + room_size / 2, connected_y + room_size / 2,
                                                    fill="black", width=2)
                        
        except Exception as e:
            logger.error(f"Error generating dungeon: {e}")
            messagebox.showerror("Error", f"Failed to generate dungeon: {e}")

    def open_drawing_tools(self):
        try:
            drawing_window = tk.Toplevel(self)
            drawing_window.title("Map Drawing Tools")

            self.drawing_canvas_widget = tk.Canvas(drawing_window, bg='white', width=800, height=600)
            self.drawing_canvas_widget.pack(fill='both', expand=True)

            self.drawing_image = Image.new("RGB", (800, 600), "white")
            self.draw = ImageDraw.Draw(self.drawing_image)

            self.current_tool = tk.StringVar(value='pencil')
            self.current_color = '#000000'

            toolbar = ttk.Frame(drawing_window)
            toolbar.pack(fill='x')

            tools = ['pencil', 'line', 'rectangle', 'oval']
            for tool in tools:
                ttk.Radiobutton(toolbar, text=tool.capitalize(), variable=self.current_tool, value=tool).pack(side='left', padx=2)

            color_button = ttk.Button(toolbar, text="Select Color", command=self.select_color)
            color_button.pack(side='left', padx=5)

            save_button = ttk.Button(toolbar, text="Save Drawing", command=lambda: self.save_drawing(drawing_window))
            save_button.pack(side='right', padx=5)

            self.drawing_canvas_widget.bind("<ButtonPress-1>", self.start_draw)
            self.drawing_canvas_widget.bind("<B1-Motion>", self.draw_motion)
            self.drawing_canvas_widget.bind("<ButtonRelease-1>", self.end_draw)

            self.drawing_start_x = None
            self.drawing_start_y = None
            self.current_drawn_item = None
        except Exception as e:
            logger.error(f"Error opening drawing tools: {e}")
            messagebox.showerror("Error", f"Failed to open drawing tools: {e}")

    def save_drawing(self, window):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All Files", "*.*")]
            )
            if file_path:
                self.drawing_image.save(file_path)
                messagebox.showinfo("Saved", f"Drawing saved to {file_path}")
                window.destroy()
        except Exception as e:
            logger.error(f"Error saving drawing: {e}")
            messagebox.showerror("Error", f"Failed to save drawing: {e}")

    def select_color(self):
        try:
            color = colorchooser.askcolor()[1]
            if color:
                self.current_color = color
        except Exception as e:
            logger.error(f"Error selecting color: {e}")
            messagebox.showerror("Error", f"Failed to select color: {e}")

    def start_draw(self, event):
        try:
            self.drawing_start_x = event.x
            self.drawing_start_y = event.y
            if self.current_tool.get() == 'pencil':
                self.drawing_canvas_widget.create_line(event.x, event.y, event.x+1, event.y+1, fill=self.current_color, width=2)
                self.draw.line([event.x, event.y, event.x+1, event.y+1], fill=self.current_color, width=2)
        except Exception as e:
            logger.error(f"Error starting draw: {e}")
            messagebox.showerror("Error", f"Failed to start drawing: {e}")

    def draw_motion(self, event):
        try:
            if self.current_tool.get() == 'pencil':
                self.drawing_canvas_widget.create_line(self.drawing_start_x, self.drawing_start_y, event.x, event.y, fill=self.current_color, width=2)
                self.draw.line([self.drawing_start_x, self.drawing_start_y, event.x, event.y], fill=self.current_color, width=2)
                self.drawing_start_x = event.x
                self.drawing_start_y = event.y
            else:
                if self.current_drawn_item:
                    self.drawing_canvas_widget.delete(self.current_drawn_item)
                if self.current_tool.get() == 'line':
                    self.current_drawn_item = self.drawing_canvas_widget.create_line(self.drawing_start_x, self.drawing_start_y, event.x, event.y, fill=self.current_color, width=2)
                elif self.current_tool.get() == 'rectangle':
                    self.current_drawn_item = self.drawing_canvas_widget.create_rectangle(self.drawing_start_x, self.drawing_start_y, event.x, event.y, outline=self.current_color, width=2)
                elif self.current_tool.get() == 'oval':
                    self.current_drawn_item = self.drawing_canvas_widget.create_oval(self.drawing_start_x, self.drawing_start_y, event.x, event.y, outline=self.current_color, width=2)
        except Exception as e:
            logger.error(f"Error during draw motion: {e}")
            messagebox.showerror("Error", f"Failed during drawing: {e}")

    def end_draw(self, event):
        try:
            if self.current_tool.get() in ['line', 'rectangle', 'oval']:
                x0, y0 = min(self.drawing_start_x, event.x), min(self.drawing_start_y, event.y)
                x1, y1 = max(self.drawing_start_x, event.x), max(self.drawing_start_y, event.y)
                if self.current_tool.get() == 'line':
                    self.draw.line([x0, y0, x1, y1], fill=self.current_color, width=2)
                elif self.current_tool.get() == 'rectangle':
                    self.draw.rectangle([x0, y0, x1, y1], outline=self.current_color, width=2)
                elif self.current_tool.get() == 'oval':
                    self.draw.ellipse([x0, y0, x1, y1], outline=self.current_color, width=2)
                self.current_drawn_item = None
        except Exception as e:
            logger.error(f"Error ending draw: {e}")
            messagebox.showerror("Error", f"Failed to end drawing: {e}")

    def edit_map(self):
        try:
            selection = self.maps_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selection Error", "Please select a map to edit.")
                return
            
            index = selection[0]
            records = self.db.get_maps()
            selected_record = records[index]
            map_id = selected_record['id']

            # Create edit dialog
            edit_dialog = tk.Toplevel(self)
            edit_dialog.title("Edit Map")

            fields = ["Name", "Campaign", "World", "Location", "Adventure", "Theme", "Description"]
            entries = {}

            for i, field in enumerate(fields):
                ttk.Label(edit_dialog, text=f"{field}:").grid(row=i, column=0, sticky='w', pady=2, padx=5)
                entry = ttk.Entry(edit_dialog, width=50)
                entry.grid(row=i, column=1, pady=2, padx=5)
                entry.insert(0, selected_record[field.lower()])
                entries[field.lower()] = entry

            def save_changes():
                try:
                    new_data = {field.lower(): entries[field.lower()].get() for field in fields}
                    self.db.update_map(map_id, new_data['name'], new_data['campaign'], new_data['world'],
                                      new_data['location'], new_data['adventure'], new_data['theme'],
                                      new_data['description'])
                    messagebox.showinfo("Success", "Map updated successfully.")
                    edit_dialog.destroy()
                    self.populate_maps_listbox()
                    self.chat_manager.rebuild_faiss_index()
                except Exception as e:
                    logger.error(f"Failed to update map: {e}")
                    messagebox.showerror("Error", f"Failed to update map: {e}")

            save_button = ttk.Button(edit_dialog, text="Save Changes", command=save_changes)
            save_button.grid(row=len(fields), column=1, sticky='e', pady=10, padx=5)

        except Exception as e:
            logger.error(f"Error editing map: {e}")
            messagebox.showerror("Error", f"Failed to edit map: {e}")

    def delete_map(self):
        try:
            selection = self.maps_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selection Error", "Please select a map to delete.")
                return
            
            index = selection[0]
            records = self.db.get_maps()
            selected_record = records[index]
            map_id = selected_record['id']
            map_name = selected_record['name']

            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the map '{map_name}'?")
            if confirm:
                self.db.delete_map(map_id)
                messagebox.showinfo("Success", f"Map '{map_name}' deleted successfully.")
                self.populate_maps_listbox()
                self.chat_manager.rebuild_faiss_index()
        except Exception as e:
            logger.error(f"Error deleting map: {e}")
            messagebox.showerror("Error", f"Failed to delete map: {e}")
