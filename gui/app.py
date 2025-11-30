import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from models.models import *
from models.constants import DEVICE_TYPES
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
        if not self.place:
            return
        name = simpledialog.askstring("Add Scene", "Scene name:")
        location = simpledialog.askstring("Scene Location", "Enter location:") if name else None
        if name and location:
            self.place.scenes.append(Scene(name=name, location=location))
            self.refresh_dsl_preview()

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
            lines.append("        do ...")
            lines.append("    end\n")

        lines.append("end")
        return "\n".join(lines)


    # -----------------------------
    # Utilities
    # -----------------------------
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
