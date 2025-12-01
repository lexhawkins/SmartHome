import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from models.models import *
from models.constants import DEVICE_TYPES, DEVICE_FUNCTIONALITIES, ACTIONS_WITH_ARGS
import os
import re

class SmartHomeApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.place = None
        self.place_file = None

        # Window setup
        self.title("SmartHome DSL Editor")
        self.geometry("1000x600")
        self.minsize(900, 500)

        # Layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # Panels
        self.create_left_panel()
        self.create_right_panel()

        # Initial prompt
        self.prompt_place_setup()

    # -----------------------------
    # Left Panel
    # -----------------------------
    def create_left_panel(self):
        frame = ttk.Frame(self, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="SmartHome DSL Editor", font=("Arial", 16, "bold")).pack(
            anchor="w", pady=(0, 10)
        )

        # Locations
        ttk.Label(frame, text="Locations", font=("Arial", 12, "bold")).pack(anchor="w")
        self.location_list = tk.Listbox(frame, height=10)
        self.location_list.pack(fill="x", pady=5)

        self.btn_add_location = ttk.Button(frame, text="Add Location", command=self.add_location)
        self.btn_remove_location = ttk.Button(frame, text="Remove Location", command=self.remove_location)
        self.btn_add_location.pack(fill="x", pady=2)
        self.btn_remove_location.pack(fill="x", pady=2)

        # Devices
        ttk.Label(frame, text="Devices", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        self.btn_add_device = ttk.Button(frame, text="Add Device", command=self.add_device)
        self.btn_remove_device = ttk.Button(frame, text="Remove Device", command=self.remove_device)
        self.btn_add_device.pack(fill="x", pady=2)
        self.btn_remove_device.pack(fill="x", pady=2)
        self.btn_view_devices = ttk.Button(frame, text="See All Devices", command=self.show_all_devices)
        self.btn_view_devices.pack(fill="x", pady=2)

        # Rules & Scenes
        ttk.Label(frame, text="Rules & Scenes", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        self.btn_add_rule = ttk.Button(frame, text="Add Rule", command=self.add_rule)
        self.btn_add_scene = ttk.Button(frame, text="Add Scene", command=self.add_scene)
        self.btn_add_rule.pack(fill="x", pady=2)
        self.btn_add_scene.pack(fill="x", pady=2)

        # File actions
        ttk.Separator(frame).pack(fill="x", pady=8)
        ttk.Label(frame, text="File Operations", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        self.btn_create_new = ttk.Button(frame, text="Create New File", command=self.create_new_file)
        self.btn_save = ttk.Button(frame, text="Save file", command=self.save_place_to_file)
        self.btn_save_as = ttk.Button(frame, text="Save As...", command=self.save_place_as)
        self.btn_open = ttk.Button(frame, text="Open...", command=self.open_place_file)
        self.btn_create_new.pack(fill="x", pady=2)
        self.btn_save.pack(fill="x", pady=2)
        self.btn_save_as.pack(fill="x", pady=2)
        self.btn_open.pack(fill="x", pady=2)

        self.disable_all_actions()

    # -----------------------------
    # Right Panel (DSL Preview)
    # -----------------------------
    def create_right_panel(self):
        frame = ttk.Frame(self, padding=10)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        ttk.Label(frame, text="DSL Preview", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.preview_text = tk.Text(frame, wrap="word", state="disabled")
        self.preview_text.grid(row=1, column=0, sticky="nsew")

    # -----------------------------
    # Place Setup
    # -----------------------------
    def prompt_place_setup(self):
        choice = messagebox.askyesno("Place Setup", "Do you want to create a new Place? (No = Open existing)")
        filename = None

        if choice:
            filename = filedialog.asksaveasfilename(title="Create Place File", defaultextension=".shl",
                                                    filetypes=[("SmartHome DSL", "*.shl")])
            if filename:
                base_name = os.path.splitext(os.path.basename(filename))[0]
                self.place = Place(base_name)
                self.place_file = filename
                self.place.locations = []
                self.place.rules = []
                self.place.scenes = []
                self.save_place_to_file()
        else:
            filename = filedialog.askopenfilename(title="Open Place File", filetypes=[("SmartHome DSL", "*.shl")])
            if filename:
                self.load_place_from_file(filename)

        if not self.place:
            messagebox.showerror("Error", "You must define a Place to continue.")
            self.destroy()
            return

        self.refresh_locations_list()
        self.refresh_dsl_preview()
        self.enable_all_actions()

    # -----------------------------
    # Enable/Disable Buttons
    # -----------------------------
    def disable_all_actions(self):
        for btn_name in [attr for attr in dir(self) if attr.startswith("btn_")]:
            btn = getattr(self, btn_name)
            try:
                btn.config(state="disabled")
            except Exception:
                pass
        try:
            self.btn_open.config(state="normal")
            self.btn_save_as.config(state="normal")
        except Exception:
            pass

    def enable_all_actions(self):
        for btn_name in [attr for attr in dir(self) if attr.startswith("btn_")]:
            btn = getattr(self, btn_name)
            try:
                btn.config(state="normal")
            except Exception:
                pass

    # -----------------------------
    # Location Handlers
    # -----------------------------
    def add_location(self):
        if not self.place:
            return

        dlg = tk.Toplevel(self)
        dlg.title("Add Location")

        # Make dialog modal and always on top
        dlg.transient(self)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        # Layout
        dlg.columnconfigure(0, weight=1)

        ttk.Label(dlg, text="Location name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = ttk.Entry(dlg)
        name_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        name_entry.focus_set()

        def save_location():
            name = name_entry.get().strip().replace(" ", "")
            if not name:
                messagebox.showerror("Error", "Location name cannot be empty.", parent=dlg)
                return

            if any(loc.name.lower() == name.lower() for loc in self.place.locations):
                messagebox.showerror("Error", f"Location '{name}' already exists.", parent=dlg)
                return

            self.place.locations.append(Location(name=name))
            self.refresh_locations_list()
            self.refresh_dsl_preview()
            dlg.destroy()

        ttk.Button(dlg, text="Add", command=save_location).grid(row=2, column=0, padx=10, pady=10)

        # Center the dialog and set a minimum size
        dlg.update_idletasks()
        width = 300
        height = dlg.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        dlg.geometry(f'{width}x{height}+{x}+{y}')
        dlg.minsize(width, height)

        self.wait_window(dlg)

    def remove_location(self):
        idx = self.get_selected_index(self.location_list)
        if idx is not None and messagebox.askyesno("Remove Location", "Are you sure?"):
            del self.place.locations[idx]
            self.refresh_locations_list()
            self.refresh_dsl_preview()

    def refresh_locations_list(self):
        self.location_list.delete(0, tk.END)
        for loc in getattr(self.place, "locations", []):
            self.location_list.insert(tk.END, loc.name)

    # -----------------------------
    # Device Handlers
    # -----------------------------
    # TODO: Update to support device types
    # TODO: DOCUMENT CHANGE
    def add_device(self):
        if not self.place or not self.place.locations:
            messagebox.showwarning("Error", "Create at least one location first.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Add Device")

        # Make dialog modal and always on top
        dlg.transient(self)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        # Configure grid layout
        dlg.columnconfigure(0, weight=1)
        dlg.columnconfigure(1, weight=2)

        ttk.Label(dlg, text="Select Device Type:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        dev_type_combo = ttk.Combobox(dlg, values=DEVICE_TYPES, state="readonly")
        dev_type_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(dlg, text="Device Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        name_entry = ttk.Entry(dlg)
        name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(dlg, text="Select Location:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        loc_combo = ttk.Combobox(dlg, values=[loc.name for loc in self.place.locations], state="readonly")
        loc_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        if loc_combo["values"]:
            loc_combo.current(0)

        def save_device():
            device_type = dev_type_combo.get()
            if not device_type:
                messagebox.showerror("Error", "Device type required.", parent=dlg)
                return
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Device name required.", parent=dlg)
                return
            location = next((l for l in self.place.locations if l.name == loc_combo.get()), None)
            if location:
                location.add_device(Device(name=name, device_type=device_type))
                self.refresh_dsl_preview()
            dlg.destroy()

        ttk.Button(dlg, text="Add", command=save_device).grid(row=3, column=0, columnspan=2, pady=10)

        # Center the dialog on the screen
        dlg.update_idletasks() # Update "requested size"
        width = 350
        height = dlg.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        dlg.geometry(f'{width}x{height}+{x}+{y}')
        dlg.minsize(width, height)

        # Wait for the dialog to be closed before returning
        self.wait_window(dlg)

    def remove_device(self):
        if not self.place or not self.place.locations:
            return
        loc_names = [loc.name for loc in self.place.locations if getattr(loc, "devices", [])]
        if not loc_names:
            messagebox.showwarning("No Devices", "There are no devices to remove.")
            return
        loc_name = simpledialog.askstring("Remove Device", f"Enter location ({', '.join(loc_names)}):")
        if not loc_name:
            return
        location = next((l for l in self.place.locations if l.name == loc_name), None)
        if location and getattr(location, "devices", []):
            location.devices.pop()
            self.refresh_dsl_preview()

    def show_all_devices(self):
        if not self.place:
            return

        dlg = tk.Toplevel(self)
        dlg.title("All Devices")
        dlg.transient(self)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        dlg.columnconfigure(0, weight=1)
        dlg.rowconfigure(1, weight=1)

        ttk.Label(dlg, text="All Devices", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        container = ttk.LabelFrame(dlg, text="Devices")
        container.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        device_listbox = tk.Listbox(container, height=10)
        empty_label = ttk.Label(container, text="No devices created yet.")
        device_items = []

        def refresh_device_list():
            device_items.clear()
            device_listbox.delete(0, tk.END)
            devices = self.get_all_devices()
            if devices:
                empty_label.grid_forget()
                device_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
                for dev, loc in devices:
                    device_items.append((dev, loc))
                    loc_name = loc.name if loc else "No Location"
                    device_listbox.insert(tk.END, f"{dev.name} ({dev.device_type}) - {loc_name}")
            else:
                device_listbox.grid_forget()
                empty_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        def edit_selected_device():
            if not device_items:
                messagebox.showinfo("No Devices", "There are no devices to edit.", parent=dlg)
                return
            idx = self.get_selected_index(device_listbox)
            if idx is None:
                messagebox.showwarning("Select Device", "Please select a device to edit.", parent=dlg)
                return
            device, location = device_items[idx]
            self.open_edit_device_dialog(device, location, on_save=refresh_device_list, parent=dlg)

        refresh_device_list()

        ttk.Button(dlg, text="Edit Device", command=edit_selected_device).grid(row=2, column=0, padx=10, pady=(5, 10), sticky="e")

        dlg.update_idletasks()
        dlg.minsize(380, dlg.winfo_reqheight())
        self.wait_window(dlg)

    # -----------------------------
    # Rules & Scenes
    # -----------------------------
    def add_rule(self):
        if not self.place:
            return
        name = simpledialog.askstring("Add Rule", "Rule name:")
        condition = simpledialog.askstring("Rule Condition", "Enter condition:") if name else None
        if name and condition:
            self.place.rules.append(Rule(name=name, condition=condition))
            self.refresh_dsl_preview()

    def add_scene(self):
        if not self.place or not self.place.locations:
            messagebox.showwarning("No Locations", "Please create a location before adding a scene.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Add Scene")
        dlg.transient(self)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        dlg.columnconfigure(1, weight=1)

        # Location
        ttk.Label(dlg, text="Location:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        loc_combo = ttk.Combobox(dlg, values=[loc.name for loc in self.place.locations], state="readonly")
        loc_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Scene Name
        ttk.Label(dlg, text="Scene Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        name_entry = ttk.Entry(dlg)
        name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Actions Frame
        actions_frame = ttk.LabelFrame(dlg, text="Actions")
        actions_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        actions_frame.columnconfigure(1, weight=1)

        actions = []
        
        def add_action_row():
            row_index = len(actions)
            
            ttk.Label(actions_frame, text="do:").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
            
            device_combo = ttk.Combobox(actions_frame, state="readonly")
            device_combo.grid(row=row_index, column=1, padx=5, pady=5, sticky="ew")

            action_combo = ttk.Combobox(actions_frame, state="readonly")
            action_combo.grid(row=row_index, column=2, padx=5, pady=5, sticky="ew")
            
            arg_frame = ttk.Frame(actions_frame)
            arg_frame.grid(row=row_index, column=3, padx=5, pady=5, sticky="ew")

            actions.append({'device_combo': device_combo, 'action_combo': action_combo, 'arg_frame': arg_frame, 'arg_widget': None})

            def on_device_select(event):
                selected_device_name = device_combo.get()
                # Clear previous action and arg
                selected_loc_name = loc_combo.get()
                location = next((l for l in self.place.locations if l.name == selected_loc_name), None)
                device = next((d for d in location.devices if d.name == selected_device_name), None)
                if device:
                    action_combo['values'] = DEVICE_FUNCTIONALITIES.get(device.device_type, [])
                    action_combo.current(0 if action_combo['values'] else -1)

            def on_action_select(event):
                action_name = action_combo.get()
                action_set = next(item for item in actions if item['action_combo'] == action_combo)

                # Clear previous arg widget
                if action_set['arg_widget']:
                    action_set['arg_widget'].destroy()
                    action_set['arg_widget'] = None

                if action_name in ACTIONS_WITH_ARGS:
                    arg_type = ACTIONS_WITH_ARGS[action_name]
                    arg_entry = ttk.Entry(action_set['arg_frame'])
                    arg_entry.pack(fill="x", expand=True)
                    arg_entry.insert(0, f"<{arg_type}>")
                    action_set['arg_widget'] = arg_entry

            action_combo.bind("<<ComboboxSelected>>", on_action_select)

            # If a location is already selected, populate this new row's device list
            selected_loc_name = loc_combo.get()
            if selected_loc_name:
                location = next((l for l in self.place.locations if l.name == selected_loc_name), None)
                if location:
                    device_names = [dev.name for dev in getattr(location, "devices", [])]
                    device_combo['values'] = device_names


            device_combo.bind("<<ComboboxSelected>>", on_device_select)

        def on_location_select(event):
            loc_name = loc_combo.get()
            location = next((l for l in self.place.locations if l.name == loc_name), None)
            if location:
                device_names = [dev.name for dev in getattr(location, "devices", [])]
                for action_set in actions:
                    action_set['device_combo']['values'] = device_names
                    action_set['device_combo'].set('')
                    action_set['action_combo'].set('')
                    action_set['action_combo']['values'] = []

        loc_combo.bind("<<ComboboxSelected>>", on_location_select)

        add_action_row() # Start with one action row

        ttk.Button(actions_frame, text="+", command=add_action_row, width=2).grid(row=100, column=2, padx=5, pady=5, sticky="e")

        def save_scene():
            name = name_entry.get().strip()
            loc_name = loc_combo.get()
            if not name or not loc_name:
                messagebox.showerror("Error", "Scene Name and Location are required.", parent=dlg)
                return

            scene_actions = []
            for action_set in actions:
                device_name = action_set['device_combo'].get()
                action_name = action_set['action_combo'].get()
                if device_name and action_name:
                    arg_widget = action_set.get('arg_widget')
                    if arg_widget:
                        arg_value = arg_widget.get()
                        scene_actions.append(f"{device_name} {action_name} {arg_value}")
                    else:
                        scene_actions.append(f"{device_name} {action_name}")


            scene = Scene(name=name, location=loc_name, actions=scene_actions)
            self.place.scenes.append(scene)
            self.refresh_dsl_preview()
            dlg.destroy()

        ttk.Button(dlg, text="Save Scene", command=save_scene).grid(row=3, column=0, columnspan=2, pady=10)

        dlg.update_idletasks()
        dlg.minsize(dlg.winfo_reqwidth(), dlg.winfo_reqheight())
        self.wait_window(dlg)

    def open_edit_device_dialog(self, device, current_location, on_save=None, parent=None):
        dlg = tk.Toplevel(self)
        dlg.title("Edit Device")
        dlg.transient(parent or self)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        dlg.columnconfigure(1, weight=1)

        ttk.Label(dlg, text="Device Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = ttk.Entry(dlg)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        name_entry.insert(0, device.name)

        ttk.Label(dlg, text="Device Type:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        device_type_combo = ttk.Combobox(dlg, values=DEVICE_TYPES, state="readonly")
        device_type_combo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        if device.device_type and device.device_type in DEVICE_TYPES:
            device_type_combo.set(device.device_type)
        elif DEVICE_TYPES:
            device_type_combo.current(0)

        ttk.Label(dlg, text="Location:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        loc_combo = ttk.Combobox(dlg, values=[loc.name for loc in self.place.locations], state="readonly")
        loc_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        if current_location:
            loc_combo.set(current_location.name)
        elif loc_combo["values"]:
            loc_combo.current(0)

        def save_changes():
            new_name = name_entry.get().strip()
            new_type = device_type_combo.get()
            loc_name = loc_combo.get()

            if not new_name or not new_type or not loc_name:
                messagebox.showerror("Error", "All fields are required.", parent=dlg)
                return

            target_location = next((l for l in self.place.locations if l.name == loc_name), None)
            if not target_location:
                messagebox.showerror("Error", "Selected location does not exist.", parent=dlg)
                return

            device.name = new_name
            device.device_type = new_type

            if current_location and target_location.id != current_location.id:
                current_location.remove_device(device)
                target_location.add_device(device)
            elif not current_location:
                target_location.add_device(device)
            else:
                device.location = target_location

            if on_save:
                on_save()
            self.refresh_dsl_preview()
            dlg.destroy()

        ttk.Button(dlg, text="Save Changes", command=save_changes).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        dlg.update_idletasks()
        dlg.minsize(350, dlg.winfo_reqheight())
        self.wait_window(dlg)

    # -----------------------------
    # DSL Preview
    # -----------------------------
    def refresh_dsl_preview(self):
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", self.generate_dsl_text())
        self.preview_text.config(state="disabled")

    def generate_dsl_text(self):
        if not self.place:
            return ""
        
        lines = [f"place {self.place.name}:", "    // Locations"]

        # Locations & devices
        for loc in getattr(self.place, "locations", []):
            lines.append(f"    location {loc.name}:")
            for dev in getattr(loc, "devices", []):
                # Updated format to match new grammar: device Name: DeviceType
                lines.append(f"        device {dev.name}: {dev.device_type}")
            lines.append("    end\n")

        # Rules
        lines.append("    // Rules")
        for rule in getattr(self.place, "rules", []):
            lines.append(f'    rule "{rule.name}":')
            lines.append(f"        when {rule.condition}")
            lines.append("    end\n")

        # Scenes
        lines.append("    // Scenes")
        for scene in getattr(self.place, "scenes", []):
            lines.append(f'    scene "{scene.name}" at {scene.location}:')
            for action in getattr(scene, 'actions', []):
                lines.append(f"        do {action}")  # Each action starts with 'do'
            lines.append("    end\n")


        lines.append("end")
        return "\n".join(lines)


    # -----------------------------
    # Utilities
    # -----------------------------
    def get_all_devices(self):
        devices = []
        for loc in getattr(self.place, "locations", []):
            for dev in getattr(loc, "devices", []):
                devices.append((dev, loc))
        return devices

    def get_selected_index(self, listbox):
        try:
            return listbox.curselection()[0]
        except IndexError:
            return None

    # -----------------------------
    # File Handling
    # -----------------------------
    def load_place_from_file(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                text = f.read()
            self.place = self.parse_dsl(text)
            self.place_file = filename
            self.refresh_locations_list()
            self.refresh_dsl_preview()
            messagebox.showinfo("Place Loaded", f"Loaded place '{self.place.name}'")
            self.enable_all_actions()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def save_place_to_file(self):
        if not getattr(self, "place_file", None):
            return self.save_place_as()
        try:
            with open(self.place_file, "w", encoding="utf-8") as f:
                f.write(self.generate_dsl_text())
            messagebox.showinfo("Saved", f"Place saved to {self.place_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def save_place_as(self):
        filename = filedialog.asksaveasfilename(title="Save Place File", defaultextension=".shl",
                                                filetypes=[("SmartHome DSL", "*.shl")])
        if filename:
            self.place_file = filename
            self.save_place_to_file()

    def open_place_file(self):
        filename = filedialog.askopenfilename(title="Open Place File", filetypes=[("SmartHome DSL", "*.shl")])
        if filename:
            self.load_place_from_file(filename)

    def create_new_file(self):
        filename = filedialog.asksaveasfilename(title="Create Place File", defaultextension=".shl",
                                                filetypes=[("SmartHome DSL", "*.shl")])
        if filename:
            base_name = os.path.splitext(os.path.basename(filename))[0]
            self.place = Place(base_name)
            self.place_file = filename
            self.place.locations = []
            self.place.rules = []
            self.place.scenes = []
            self.save_place_to_file()
            self.refresh_locations_list()
            self.refresh_dsl_preview()
            self.enable_all_actions()

    # -----------------------------
    # DSL Parsing
    # -----------------------------
    def parse_dsl(self, text):
        lines = [l.split("//")[0].rstrip() for l in text.splitlines() if l.strip()]
        place = None
        current_loc = None
        re_place = re.compile(r"^\s*place\s+([A-Za-z0-9_\-]+)\s*:", re.IGNORECASE)
        re_location = re.compile(r"^\s*location\s+([A-Za-z0-9_\-]+)\s*:\s*$", re.IGNORECASE)
        re_device = re.compile(r"^\s*device\s+([A-Za-z0-9_\-]+)\s*:\s*([A-Za-z0-9_\-]+)\s*$", re.IGNORECASE)

        for line in lines:
            line = line.strip()
            if m := re_place.match(line):
                place = Place(m.group(1))
                place.locations, place.rules, place.scenes = [], [], []
                continue
            if m := re_location.match(line):
                loc_name = m.group(1)
                if not loc_name:
                    loc_name = "UnnamedLocation"
                current_loc = Location(name=loc_name)
                place.locations.append(current_loc)
                continue
            if current_loc and (m := re_device.match(line)):
                current_loc.devices.append(Device(name=m.group(1), device_type=m.group(2)))


        if not place:
            place = Place(name=os.path.splitext(os.path.basename(self.place_file or "UnnamedPlace.shl"))[0])
            place.locations, place.rules, place.scenes = [], [], []
        return place


if __name__ == "__main__":
    app = SmartHomeApp()
    app.mainloop()
