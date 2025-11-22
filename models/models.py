from dataclasses import dataclass, field
from typing import List, Optional
import uuid


def uid() -> str:
    return str(uuid.uuid4())


# -----------------------
# Device
# -----------------------
@dataclass
class Device:
    id: str = field(default_factory=uid)
    name: str = ""
    device_type: str = ""
    location: Optional["Location"] = None  # Actual object reference

    def __str__(self):
        loc = self.location.name if self.location else "No Location"
        return f"{self.name} ({self.device_type}) @ {loc}"


# -----------------------
# Location
# -----------------------
@dataclass
class Location:
    id: str = field(default_factory=uid)
    name: str = ""
    devices: List[Device] = field(default_factory=list)

    def add_device(self, device: Device):
        device.location = self
        self.devices.append(device)

    def remove_device(self, device: Device):
        self.devices = [d for d in self.devices if d.id != device.id]

    def __str__(self):
        return self.name


# -----------------------
# Rule
# -----------------------
@dataclass
class Rule:
    id: str = field(default_factory=uid)
    name: str = ""
    condition: str = ""  # DSL condition
    actions: List[str] = field(default_factory=list)

    def __str__(self):
        return self.name


# -----------------------
# Scene
# -----------------------
@dataclass
class Scene:
    id: str = field(default_factory=uid)
    name: str = ""
    location: str = ""  # keep as a string for now; can convert later
    actions: List[str] = field(default_factory=list)

    def __str__(self):
        return f"{self.name} @ {self.location}"


# -----------------------
# Place
# -----------------------
@dataclass
class Place:
    name: str
    id: str = field(default_factory=uid)
    locations: List[Location] = field(default_factory=list)
    rules: List[Rule] = field(default_factory=list)
    scenes: List[Scene] = field(default_factory=list)
