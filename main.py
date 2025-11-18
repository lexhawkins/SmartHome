import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
from typing import List


# =========================
#  MODELO (DOMINIO)
# =========================

@dataclass
class Device:
    name: str
    device_type: str
    location: str


@dataclass
class Rule:
    name: str
    condition: str              # texto DSL de la condición (sin la palabra 'when')
    actions: List[str] = field(default_factory=list)  # cada acción: 'Device command [value]'


@dataclass
class Scene:
    name: str
    # luego agregamos lista de acciones
    pass


# =========================
#  APLICACIÓN
# =========================

class SmartHomeApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Config básica de la ventana ---
        self.title("SmartHome DSL Editor")
        self.geometry("1000x600")  # ancho x alto
        self.minsize(800, 500)

        # Listas internas (modelo)
        self.devices: List[Device] = []
        self.rules: List[Rule] = []
        self.scenes: List[Scene] = []

        # Widgets
        self.devices_listbox = None
        self.rules_listbox = None
        self.scenes_listbox = None
        self.preview_text = None

        # Construir interfaz
        self._create_widgets()

    # ---------------------------
    # Layout / Widgets
    # ---------------------------
    def _create_widgets(self):
        # Layout principal: 2 columnas
        self.columnconfigure(0, weight=1)  # izquierda
        self.columnconfigure(1, weight=2)  # derecha
        self.rowconfigure(0, weight=1)

        # --------- PANEL IZQUIERDO ----------
        left_frame = ttk.Frame(self, padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew")

        title_lbl = ttk.Label(left_frame, text="SmartHome DSL Editor",
                              font=("Segoe UI", 18, "bold"))
        title_lbl.pack(anchor="w", pady=(0, 10))

        # Botones de acciones principales
        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(buttons_frame, text="+ Add Device",
                   command=self.open_add_device_window).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="+ Add Rule",
                   command=self.open_add_rule_window).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="+ Add Scene",
                   command=self.not_implemented_yet).pack(side="left", padx=5)

        # ---- Devices ----
        devices_label = ttk.Label(left_frame, text="Devices", font=("Segoe UI", 12, "bold"))
        devices_label.pack(anchor="w", pady=(10, 0))

        self.devices_listbox = tk.Listbox(left_frame, height=8)
        self.devices_listbox.pack(fill="x", pady=5)

        # ---- Rules ----
        rules_label = ttk.Label(left_frame, text="Rules", font=("Segoe UI", 12, "bold"))
        rules_label.pack(anchor="w", pady=(10, 0))

        self.rules_listbox = tk.Listbox(left_frame, height=5)
        self.rules_listbox.pack(fill="x", pady=5)

        # ---- Scenes ----
        scenes_label = ttk.Label(left_frame, text="Scenes", font=("Segoe UI", 12, "bold"))
        scenes_label.pack(anchor="w", pady=(10, 0))

        self.scenes_listbox = tk.Listbox(left_frame, height=5)
        self.scenes_listbox.pack(fill="x", pady=5)

        # --------- PANEL DERECHO ----------
        right_frame = ttk.Frame(self, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")

        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        preview_label = ttk.Label(right_frame, text="DSL Preview",
                                  font=("Segoe UI", 12, "bold"))
        preview_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.preview_text = tk.Text(right_frame, wrap="word")
        self.preview_text.grid(row=1, column=0, sticky="nsew")
        self.preview_text.config(state="disabled")  # solo lectura

    # ---------------------------
    # Ventana "Add Device"
    # ---------------------------
    def open_add_device_window(self):
        """Abre una ventana emergente para crear un dispositivo."""
        win = tk.Toplevel(self)
        win.title("Add Device")
        win.grab_set()  # foco en esta ventana

        ttk.Label(win, text="Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name_entry = ttk.Entry(win, width=25)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(win, text="Type:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        device_types = [
            "Light", "Sensor", "AC", "Camera", "Lock",
            "Thermostat", "SmartSpeaker", "Alarm"
        ]
        type_combo = ttk.Combobox(win, values=device_types, state="readonly", width=22)
        type_combo.grid(row=1, column=1, padx=10, pady=5)
        type_combo.current(0)  # valor por defecto

        ttk.Label(win, text="Location:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        location_entry = ttk.Entry(win, width=25)
        location_entry.grid(row=2, column=1, padx=10, pady=5)

        # Botones
        btn_frame = ttk.Frame(win)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        def on_save():
            name = name_entry.get().strip()
            dtype = type_combo.get().strip()
            location = location_entry.get().strip()

            if not name or not dtype or not location:
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return

            # Crear y guardar el Device en la lista interna
            device = Device(name=name, device_type=dtype, location=location)
            self.devices.append(device)

            # Actualizar UI
            self.refresh_devices_list()
            self.refresh_dsl_preview()

            win.destroy()

        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Device", command=on_save).pack(side="left", padx=5)

    # ---------------------------
    # Ventana "Add Rule"
    # ---------------------------
    def open_add_rule_window(self):
        """Abre ventana para crear una regla (name + condition + 1 action)."""

        # Necesitamos al menos un device para que tenga sentido la regla
        if not self.devices:
            messagebox.showerror("Error", "Primero crea al menos un Device.")
            return

        win = tk.Toplevel(self)
        win.title("Add Rule")
        win.grab_set()

        # --- Nombre de la regla ---
        ttk.Label(win, text="Rule name (texto entre comillas):").grid(
            row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w"
        )
        name_entry = ttk.Entry(win, width=40)
        name_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # --- Tipo de condición ---
        ttk.Label(win, text="Condition type:").grid(
            row=2, column=0, padx=10, pady=(10, 0), sticky="w"
        )

        cond_types = [
            "Sensor detects",
            "Sensor comparison",
            "State condition",
        ]
        cond_combo = ttk.Combobox(win, values=cond_types, state="readonly", width=25)
        cond_combo.grid(row=2, column=1, padx=10, pady=(10, 0), sticky="e")
        cond_combo.current(0)

        # Frame donde dibujamos los controles específicos de la condición
        cond_frame = ttk.Frame(win, borderwidth=1, relief="groove", padding=10)
        cond_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # --- Sección para acción principal ---
        ttk.Label(win, text="Action (do ...):").grid(
            row=4, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w"
        )

        action_frame = ttk.Frame(win, borderwidth=1, relief="groove", padding=10)
        action_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # ========== Construcción dinámica de la condición ==========

        def build_sensor_detects_ui():
            # Limpia frame
            for widget in cond_frame.winfo_children():
                widget.destroy()

            sensors = [d.name for d in self.devices if d.device_type == "Sensor"]
            if not sensors:
                sensors = ["<no sensors>"]

            ttk.Label(cond_frame, text="Sensor:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            sensor_combo = ttk.Combobox(cond_frame, values=sensors, state="readonly", width=20)
            sensor_combo.grid(row=0, column=1, padx=5, pady=5)
            sensor_combo.current(0)

            ttk.Label(cond_frame, text='Event (e.g. "movement"):').grid(
                row=1, column=0, padx=5, pady=5, sticky="e"
            )
            event_entry = ttk.Entry(cond_frame, width=22)
            event_entry.grid(row=1, column=1, padx=5, pady=5)

            # Guardamos en el frame los widgets para extraer datos luego
            cond_frame.sensor_combo = sensor_combo
            cond_frame.event_entry = event_entry
            cond_frame.cond_kind = "sensor_detects"

        def build_sensor_comparison_ui():
            for widget in cond_frame.winfo_children():
                widget.destroy()

            sensors = [d.name for d in self.devices if d.device_type == "Sensor"]
            if not sensors:
                sensors = ["<no sensors>"]

            ttk.Label(cond_frame, text="Sensor:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            sensor_combo = ttk.Combobox(cond_frame, values=sensors, state="readonly", width=20)
            sensor_combo.grid(row=0, column=1, padx=5, pady=5)
            sensor_combo.current(0)

            ttk.Label(cond_frame, text="Operator:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            op_combo = ttk.Combobox(cond_frame, values=[">", "<", "="],
                                    state="readonly", width=5)
            op_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            op_combo.current(0)

            ttk.Label(cond_frame, text="Value (INT):").grid(
                row=2, column=0, padx=5, pady=5, sticky="e"
            )
            value_entry = ttk.Entry(cond_frame, width=10)
            value_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

            cond_frame.sensor_combo = sensor_combo
            cond_frame.op_combo = op_combo
            cond_frame.value_entry = value_entry
            cond_frame.cond_kind = "sensor_comparison"

        def build_state_condition_ui():
            for widget in cond_frame.winfo_children():
                widget.destroy()

            devices = [d.name for d in self.devices] or ["<no devices>"]

            ttk.Label(cond_frame, text="Device:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            device_combo = ttk.Combobox(cond_frame, values=devices, state="readonly", width=20)
            device_combo.grid(row=0, column=1, padx=5, pady=5)
            device_combo.current(0)

            ttk.Label(cond_frame, text="State:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            states = ["on", "off", "locked", "unlocked",
                      "open", "closed", "active", "inactive"]
            state_combo = ttk.Combobox(cond_frame, values=states, state="readonly", width=15)
            state_combo.grid(row=1, column=1, padx=5, pady=5)
            state_combo.current(0)

            cond_frame.device_combo = device_combo
            cond_frame.state_combo = state_combo
            cond_frame.cond_kind = "state_condition"

        # Al cambiar el tipo de condición reconstruimos el UI
        def on_condition_type_change(event=None):
            kind = cond_combo.get()
            if kind == "Sensor detects":
                build_sensor_detects_ui()
            elif kind == "Sensor comparison":
                build_sensor_comparison_ui()
            elif kind == "State condition":
                build_state_condition_ui()

        cond_combo.bind("<<ComboboxSelected>>", on_condition_type_change)
        # construimos el default
        build_sensor_detects_ui()

        # ========== UI de la acción ==========

        for widget in action_frame.winfo_children():
            widget.destroy()

        devices_names = [d.name for d in self.devices] or ["<no devices>"]
        commands = [
            "turn_on", "turn_off", "lock", "unlock",
            "set_temperature", "set_brightness", "play_music",
            "activate", "deactivate", "record", "stop", "announce"
        ]

        ttk.Label(action_frame, text="Device:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        action_device_combo = ttk.Combobox(action_frame, values=devices_names,
                                           state="readonly", width=20)
        action_device_combo.grid(row=0, column=1, padx=5, pady=5)
        action_device_combo.current(0)

        ttk.Label(action_frame, text="Command:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        action_command_combo = ttk.Combobox(action_frame, values=commands,
                                            state="readonly", width=20)
        action_command_combo.grid(row=1, column=1, padx=5, pady=5)
        action_command_combo.current(0)

        ttk.Label(action_frame, text="Value (optional):").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        action_value_entry = ttk.Entry(action_frame, width=15)
        action_value_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Botones de guardado
        btn_frame = ttk.Frame(win)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)

        def build_condition_string():
            """Construye el texto DSL de la condición según el UI."""
            kind = getattr(cond_frame, "cond_kind", None)

            if kind == "sensor_detects":
                sensor = cond_frame.sensor_combo.get()
                event_text = cond_frame.event_entry.get().strip()
                if not event_text:
                    return None
                return f'{sensor} detects "{event_text}"'

            elif kind == "sensor_comparison":
                sensor = cond_frame.sensor_combo.get()
                op = cond_frame.op_combo.get()
                value = cond_frame.value_entry.get().strip()
                if not value:
                    return None
                return f"{sensor} {op} {value}"

            elif kind == "state_condition":
                device = cond_frame.device_combo.get()
                state = cond_frame.state_combo.get()
                return f"{device} is {state}"

            return None

        def on_save_rule():
            rule_name = name_entry.get().strip()
            if not rule_name:
                messagebox.showerror("Error", "La regla necesita un nombre.")
                return

            condition_str = build_condition_string()
            if not condition_str:
                messagebox.showerror("Error", "La condición está incompleta.")
                return

            # Acción
            a_device = action_device_combo.get()
            a_command = action_command_combo.get()
            a_value = action_value_entry.get().strip()

            if a_value:
                action_str = f"{a_device} {a_command} {a_value}"
            else:
                action_str = f"{a_device} {a_command}"

            new_rule = Rule(name=rule_name, condition=condition_str, actions=[action_str])
            self.rules.append(new_rule)

            self.refresh_rules_list()
            self.refresh_dsl_preview()

            win.destroy()

        ttk.Button(btn_frame, text="Cancel",
                   command=win.destroy).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Rule",
                   command=on_save_rule).pack(side="left", padx=5)

    # ---------------------------
    # Helpers para refrescar UI
    # ---------------------------
    def refresh_devices_list(self):
        """Rellena la Listbox de devices con los datos actuales."""
        self.devices_listbox.delete(0, tk.END)
        for d in self.devices:
            # Ejemplo de texto: Light1 (Light) - Living Room
            display = f"{d.name} ({d.device_type}) - {d.location}"
            self.devices_listbox.insert(tk.END, display)

    def refresh_rules_list(self):
        """Rellena la Listbox de rules."""
        self.rules_listbox.delete(0, tk.END)
        for r in self.rules:
            self.rules_listbox.insert(tk.END, f'{r.name}')

    def refresh_dsl_preview(self):
        """Genera el código DSL a partir del modelo actual."""
        lines = []

        # Devices
        for d in self.devices:
            lines.append(f"device {d.name}")
            lines.append(f"type {d.device_type}")
            lines.append(f'location "{d.location}"')
            lines.append("")  # línea en blanco

        # Rules
        for r in self.rules:
            lines.append(f'rule "{r.name}"')
            lines.append(f"when {r.condition}")
            for act in r.actions:
                lines.append(f"do {act}")
            lines.append("end")
            lines.append("")

        # (Luego agregaremos scenes aquí)

        dsl_code = "\n".join(lines)

        # Actualizar el Text como solo lectura
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", dsl_code)
        self.preview_text.config(state="disabled")

    # ---------------------------
    # Placeholders
    # ---------------------------
    def not_implemented_yet(self):
        messagebox.showinfo("Info", "La parte de Scenes la haremos en el siguiente paso.")


if __name__ == "__main__":
    app = SmartHomeApp()
    app.mainloop()
