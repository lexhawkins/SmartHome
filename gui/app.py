import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from models.models import *
from textx import metamodel_from_file
from models.constants import SENSOR_EVENTS, DEVICE_TYPES, DEVICE_FUNCTIONALITIES, DEVICE_CATEGORIES, ACTIONS_WITH_ARGS, DETECTOR_FUNCTIONALITIES
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
        self.configure(bg="#4d82bc")
        self.style = ttk.Style(self)
        self.style.configure("Main.TFrame", background="#4d82bc")
        self.style.configure("Main.TLabel", background="#4d82bc", foreground="white")

        # Layout with scrollable container
        self.setup_scrollable_layout()

        # Panels
        self.create_left_panel()
        self.create_right_panel()

        # Initial prompt
        self.prompt_place_setup()

    # -----------------------------
    # Main Layout (scrollable)
    # -----------------------------
    def setup_scrollable_layout(self):
        self.container = ttk.Frame(self, style="Main.TFrame")
        self.container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.container, highlightthickness=0, bg="#4d82bc")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.v_scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.content_frame = ttk.Frame(self.canvas, style="Main.TFrame")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        # Keep scrollregion and width synced
        self.content_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width)
        )

        # Grid weights inside scrollable area
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=2)
        self.content_frame.rowconfigure(0, weight=1)

    # -----------------------------
    # Left Panel
    # -----------------------------
    def create_left_panel(self):
        frame = ttk.Frame(self.content_frame, padding=10, style="Main.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="SmartHome DSL Editor", font=("Arial", 16, "bold"), style="Main.TLabel").pack(
            anchor="w", pady=(0, 10)
        )

        # Locations
        ttk.Label(frame, text="Locations", font=("Arial", 12, "bold"), style="Main.TLabel").pack(anchor="w")
        self.location_list = tk.Listbox(frame, height=10)
        self.location_list.pack(fill="x", pady=5)

        self.btn_add_location = ttk.Button(frame, text="Add Location", command=self.add_location)
        self.btn_remove_location = ttk.Button(frame, text="Remove Location", command=self.remove_location)
        self.btn_add_location.pack(fill="x", pady=2)
        self.btn_remove_location.pack(fill="x", pady=2)

        # Devices
        ttk.Label(frame, text="Devices", font=("Arial", 12, "bold"), style="Main.TLabel").pack(anchor="w", pady=(10, 0))
        self.btn_add_device = ttk.Button(frame, text="Add Device", command=self.add_device)
        self.btn_remove_device = ttk.Button(frame, text="Remove Device", command=self.remove_device)
        self.btn_add_device.pack(fill="x", pady=2)
        self.btn_remove_device.pack(fill="x", pady=2)
        self.btn_view_devices = ttk.Button(frame, text="See All Devices", command=self.show_all_devices)
        self.btn_view_devices.pack(fill="x", pady=2)

        # Rules & Scenes
        ttk.Label(frame, text="Rules & Scenes", font=("Arial", 12, "bold"), style="Main.TLabel").pack(anchor="w", pady=(10, 0))
        self.btn_add_rule = ttk.Button(frame, text="Add Rule", command=self.add_rule)
        self.btn_add_scene = ttk.Button(frame, text="Add Scene", command=self.add_scene)
        self.btn_add_rule.pack(fill="x", pady=2)
        self.btn_add_scene.pack(fill="x", pady=2)

        # File actions
        ttk.Separator(frame).pack(fill="x", pady=8)
        ttk.Label(frame, text="File Operations", font=("Arial", 12, "bold"), style="Main.TLabel").pack(anchor="w", pady=(10, 0))
        self.btn_create_new = ttk.Button(frame, text="Create New File", command=self.create_new_file)
        self.btn_save = ttk.Button(frame, text="Save file", command=self.save_place_to_file)
        self.btn_save_as = ttk.Button(frame, text="Save As...", command=self.save_place_as)
        self.btn_open = ttk.Button(frame, text="Open...", command=self.open_place_file)
        self.btn_create_new.pack(fill="x", pady=2)
        self.btn_save.pack(fill="x", pady=2)
        self.btn_save_as.pack(fill="x", pady=2)
        self.btn_open.pack(fill="x", pady=2)

        ttk.Separator(frame).pack(fill="x", pady=8)
        self.btn_validate = ttk.Button(frame, text="Validate and Start SmartHome", command=self.validate_and_run)
        self.btn_validate.pack(fill="x", pady=2)

        self.disable_all_actions()

    # -----------------------------
    # Right Panel (DSL Preview)
    # -----------------------------
    def create_right_panel(self):
        frame = ttk.Frame(self.content_frame, padding=10, style="Main.TFrame")
        frame.grid(row=0, column=1, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="DSL Preview", font=("Arial", 12, "bold"), style="Main.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.preview_text = tk.Text(frame, wrap="word", state="disabled")
        self.preview_text.grid(row=1, column=0, sticky="nsew")
        self.preview_text.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

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
        if not self.place or not self.place.locations:
            messagebox.showwarning("No Locations", "Create at least one location before adding rules.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Add Rule")
        dlg.transient(self)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        dlg.columnconfigure(1, weight=1)

        # -------------------
        # Rule Name
        # -------------------
        tk.Label(dlg, text="Rule Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        name_entry = tk.Entry(dlg)
        name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # -------------------
        # Condition
        # -------------------
        tk.Label(dlg, text="Condition:").grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        condition_frame = tk.Frame(dlg)
        condition_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        detector_devices = [
            d.name for loc in self.place.locations for d in loc.devices
            if d.device_type in DEVICE_CATEGORIES["Detector"]
        ]

        condition_device_combo = ttk.Combobox(condition_frame, values=detector_devices, state="readonly")
        condition_device_combo.grid(row=0, column=0, padx=2, pady=2)

        condition_type_combo = ttk.Combobox(condition_frame, state="readonly")
        condition_type_combo.grid(row=0, column=1, padx=2, pady=2)

        # New combobox for thermostat functionality (temperature)
        thermo_func_combo = ttk.Combobox(condition_frame, values=["temperature"], state="readonly")
        thermo_func_combo.grid(row=0, column=2, padx=2, pady=2)
        thermo_func_combo.grid_remove()

        # Sensor events
        sensor_event_combo = ttk.Combobox(condition_frame, values=SENSOR_EVENTS, state="readonly")
        sensor_event_combo.grid(row=0, column=2, padx=2, pady=2)
        sensor_event_combo.grid_remove()

        # Comparison operators
        comparison_combo = ttk.Combobox(condition_frame, values=["<", ">", "="], width=3, state="readonly")
        comparison_combo.grid(row=0, column=3, padx=2, pady=2)
        comparison_combo.grid_remove()

        # Value entry
        extra_arg_entry = tk.Entry(condition_frame)
        extra_arg_entry.grid(row=0, column=4, padx=2, pady=2)
        extra_arg_entry.grid_remove()

        def update_condition_options(event=None):
            device_name = condition_device_combo.get()
            device = next(
                (d for loc in self.place.locations for d in loc.devices if d.name == device_name),
                None
            )
            if not device:
                return

            # Reset visibility
            thermo_func_combo.grid_remove()
            sensor_event_combo.grid_remove()
            comparison_combo.grid_remove()
            extra_arg_entry.grid_remove()

            if device.device_type == "Thermostat":
                condition_type_combo["values"] = ["detects"]
                condition_type_combo.current(0)

                thermo_func_combo.grid()       # Show temperature selector
                thermo_func_combo.current(0)

                comparison_combo.grid()
                extra_arg_entry.grid()

            elif device.device_type in ["Sensor", "Camera"]:
                condition_type_combo["values"] = ["detects"]
                condition_type_combo.current(0)

                sensor_event_combo.grid()

            else:
                condition_type_combo["values"] = []

        condition_device_combo.bind("<<ComboboxSelected>>", update_condition_options)

        # -------------------
        # Actions (Do)
        # -------------------
        tk.Label(dlg, text="Do:").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        actions_frame = tk.Frame(dlg)
        actions_frame.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        all_devices = [d.name for loc in self.place.locations for d in loc.devices]
        action_rows = []

        def add_action_row():
            row_frame = tk.Frame(actions_frame)
            row_frame.pack(fill="x", pady=2)

            dev_combo = ttk.Combobox(row_frame, values=all_devices, state="readonly")
            dev_combo.pack(side="left", padx=2)

            cmd_combo = ttk.Combobox(row_frame, state="readonly")
            cmd_combo.pack(side="left", padx=2)

            arg_entry = tk.Entry(row_frame, width=15)

            def update_actions(event=None):
                dev_name = dev_combo.get()
                device = next(
                    (d for loc in self.place.locations for d in loc.devices if d.name == dev_name),
                    None
                )
                if device:
                    cmds = DEVICE_FUNCTIONALITIES.get(device.device_type, [])
                    cmd_combo["values"] = cmds
                    if not cmd_combo.get() and cmds:
                        cmd_combo.current(0)

                    selected_cmd = cmd_combo.get()
                    if ACTIONS_WITH_ARGS.get(selected_cmd):
                        arg_entry.pack(side="left", padx=2)
                    else:
                        arg_entry.pack_forget()

            dev_combo.bind("<<ComboboxSelected>>", update_actions)
            cmd_combo.bind("<<ComboboxSelected>>", update_actions)

            action_rows.append({"device": dev_combo, "action": cmd_combo, "arg": arg_entry})

        add_action_row()

        # Add + / - buttons
        btn_frame = tk.Frame(dlg)
        btn_frame.grid(row=3, column=1, sticky="e", padx=5, pady=5)

        tk.Button(btn_frame, text="+", command=add_action_row).pack(side="left", padx=2)

        def remove_last_action():
            if action_rows:
                row = action_rows.pop()
                for widget in row.values():
                    widget.destroy()

        tk.Button(btn_frame, text="-", command=remove_last_action).pack(side="left", padx=2)

        # -------------------
        # Save button
        # -------------------
        def save_rule():
            name = name_entry.get().strip()
            dev_name = condition_device_combo.get()
            cond_type = condition_type_combo.get()

            condition_str = None
            device = next(
                (d for loc in self.place.locations for d in loc.devices if d.name == dev_name),
                None
            )

            # ---- Thermostat ----
            if device and device.device_type == "Thermostat":
                func = thermo_func_combo.get().strip()  # "temperature"
                op = comparison_combo.get().strip()
                val = extra_arg_entry.get().strip()

                if func and op and val:
                    condition_str = f"{dev_name} detects {func} {op} {val}"
                else:
                    messagebox.showerror("Error", "Please set thermostat condition (function, operator, value).", parent=dlg)
                    return

            # ---- Sensor / Camera ----
            elif device and device.device_type in ["Sensor", "Camera"]:
                event = sensor_event_combo.get().strip()
                if event:
                    condition_str = f"{dev_name} detects {event}"
                else:
                    messagebox.showerror("Error", "Please select an event for sensor/camera.", parent=dlg)
                    return

            # Collect actions
            action_list = []
            for act in action_rows:
                d = act["device"].get()
                cmd = act["action"].get()
                arg = act["arg"].get().strip()

                if arg and not arg.isnumeric() and not (arg.startswith('"') and arg.endswith('"')):
                    arg = f'"{arg}"'

                if d and cmd:
                    action_list.append(f"{d} {cmd} {arg}".strip())

            if not name or not condition_str:
                messagebox.showerror("Error", "Rule name or condition is missing.", parent=dlg)
                return

            self.place.rules.append(
                Rule(name=f'"{name}"', condition=condition_str, actions=action_list)
            )
            self.refresh_dsl_preview()
            dlg.destroy()

        tk.Button(dlg, text="Save", command=save_rule).grid(row=4, column=1, sticky="e", padx=5, pady=5)


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
        
        lines = [f"place {self.place.name}:"]

        # Locations & devices
        for loc in getattr(self.place, "locations", []):
            lines.append(f"    location {loc.name}:")
            for dev in getattr(loc, "devices", []):
                lines.append(f"        device {dev.name}: {dev.device_type}")
            lines.append("    end")

        # Rules
        lines.append("    // Rules")
        for rule in getattr(self.place, "rules", []):
            lines.append(f"    rule {rule.name}:")
            lines.append(f"        if {rule.condition}")
            for action in rule.actions:
                lines.append(f"            do {action}")
            lines.append("    end")

        # Scenes
        lines.append("    // Scenes")
        for scene in getattr(self.place, "scenes", []):
            # Scene header with quotes and location
            lines.append(f'    scene "{scene.name}" at {scene.location}:')
            for action in scene.actions:
                parts = action.split(maxsplit=2)  # e.g., "BedroomSmartSpeaker play_music Metallica"
                if len(parts) == 3:
                    device, cmd, arg = parts
                    # Add quotes if argument is not a number                    
                    if not arg.replace('.', '', 1).isdigit() and not (arg.startswith('"') and arg.endswith('"')):
                        arg = f'"{arg.strip()}"'
                    lines.append(f"        do {device} {cmd} {arg}")
                else:
                    lines.append(f"        do {action}")
            lines.append("    end")


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
        current_context = None  # Can be a location, rule, or scene

        re_place = re.compile(r"^\s*place\s+([A-Za-z0-9_\-]+)\s*:", re.IGNORECASE)
        re_location = re.compile(r"^\s*location\s+([A-Za-z0-9_\-]+)\s*:\s*$", re.IGNORECASE)
        re_device = re.compile(r"^\s*device\s+([A-Za-z0-9_\-]+)\s*:\s*([A-Za-z0-9_\-]+)\s*$", re.IGNORECASE)
        re_rule = re.compile(r"^\s*rule\s+(\".*\")\s*:", re.IGNORECASE)
        re_scene = re.compile(r"^\s*scene\s+(\".*\")\s+at\s+([A-Za-z0-9_\-]+)\s*:", re.IGNORECASE)
        re_if = re.compile(r"^\s*if\s+(.*)", re.IGNORECASE)
        re_do = re.compile(r"^\s*do\s+(.*)", re.IGNORECASE)
        re_end = re.compile(r"^\s*end\s*$", re.IGNORECASE)

        for line in lines:
            line = line.strip()

            # End of a block
            if re_end.match(line):
                if isinstance(current_context, (Location, Rule, Scene)):
                    current_context = None # Exit the current block context
                continue

            # Inside a block, process its contents
            if isinstance(current_context, Location) and (m := re_device.match(line)):
                current_context.add_device(Device(name=m.group(1), device_type=m.group(2)))
                continue
            elif isinstance(current_context, Rule) and (m := re_if.match(line)):
                current_context.condition = m.group(1).strip()
                continue
            elif isinstance(current_context, (Rule, Scene)) and (m := re_do.match(line)):
                current_context.actions.append(m.group(1).strip())
                continue

            # Top-level block definitions
            if m := re_place.match(line):
                place = Place(m.group(1))
                place.locations, place.rules, place.scenes = [], [], []
                continue
            if not place: continue

            if m := re_location.match(line):
                loc_name = m.group(1)
                current_context = Location(name=loc_name)
                place.locations.append(current_context)
                continue
            
            if m := re_rule.match(line):
                rule_name = m.group(1)
                current_context = Rule(name=rule_name)
                place.rules.append(current_context)
                continue
            
            if m := re_scene.match(line):
                scene_name, loc_name = m.groups()
                current_context = Scene(name=scene_name.strip('"'), location=loc_name)
                place.scenes.append(current_context)
                continue

        if not place:
            place = Place(name=os.path.splitext(os.path.basename(self.place_file or "UnnamedPlace.shl"))[0])
            place.locations, place.rules, place.scenes = [], [], []
        return place

    def validate_and_run(self):
        """
        Gets the DSL code from the preview text box, validates it against the
        textX grammar, and shows a status message to the user.
        """
        code = self.preview_text.get("1.0", tk.END)

        # The grammar file is in the parent directory of the 'gui' folder
        grammar_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "grammar.tx"))

        if not os.path.exists(grammar_file):
            messagebox.showerror("Error", f"Grammar file not found at: {grammar_file}")
            return

        try:
            # Create a metamodel from the grammar file
            metamodel = metamodel_from_file(grammar_file)
            # Parse the code from the editor
            metamodel.model_from_str(code)
            messagebox.showinfo("Success", "You're SmartHome program is up and running")
        except Exception as e:
            messagebox.showerror("Validation Error", f"There seem to be some errors in your program.\n\nDetails: {e}")



if __name__ == "__main__":
    app = SmartHomeApp()
    app.mainloop()