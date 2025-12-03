DEVICE_TYPES = [
    "Light",
    "Sensor", # For our purposes (and simplicity), sensors can only detect three types of events. See SENSOR_EVENTS below
    "AC",
    "Camera",
    "Lock",
    "Thermostat", # Thermostat are the only devices that can detect temperature (in real-world scenarios)
    "SmartSpeaker",
    "Alarm",
]

DEVICE_FUNCTIONALITIES = {
    "Light":            ["turn_on", "turn_off"],
    "Sensor":           ["detects"],
    "AC":               ["turn_on", "turn_off", "set_to_temperature"],
    "Camera":           ["record", "stop", "send_alert"],
    "Lock":             ["lock", "unlock"],
    "Thermostat":       ["detects_temperature"],
    "SmartSpeaker":     ["play_music", "announce"],
    "Alarm":            ["activate", "deactivate"],
}


DETECTOR_FUNCTIONALITIES = {
    "Sensor": ["detects"],
    "Thermostat": ["detects_temperature"],
    "Camera": ["detects"],
}


DEVICE_CATEGORIES = {
    "Detector": ["Camera", "Sensor", "Thermostat"],
    "Actuator": ["AC","Alarm","Camera","Light", "Lock", "SmartSpeaker"],
}

SENSOR_EVENTS = [
    "movement",
    "noise",
    "light",
]

ACTIONS_WITH_ARGS = {
    "set_to_temperature": "int",
    "play_music": "str",
    "announce": "str",
}
