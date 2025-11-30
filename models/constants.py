DEVICE_FUNCTIONALITIES = {
    "Light": ["turn_on", "turn_off", "set_brightness"],
    "Sensor": [],
    "AC": ["turn_on", "turn_off", "set_temperature"],
    "Camera": ["record", "stop"],
    "Lock": ["lock", "unlock"],
    "Thermostat": ["set_temperature"],
    "SmartSpeaker": ["play_music", "announce"],
    "Alarm": ["activate", "deactivate"],
}

DEVICE_TYPES = [
    "Light",
    "Sensor",
    "AC",
    "Camera",
    "Lock",
    "Thermostat",
    "SmartSpeaker",
    "Alarm",
]

ACTIONS_WITH_ARGS = {
    "set_brightness": "int",
    "set_temperature": "int",
    "play_music": "str",
    "announce": "str",
}
