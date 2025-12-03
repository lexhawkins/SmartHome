# SmartHome DSL & Editor

## Overview

The SmartHome DSL Editor is a graphical user interface (GUI) application built with Python and Tkinter that allows you to create and manage configurations for a our SmartHome system. It provides a user-friendly way to define places, locations, and devices, which are then saved into a custom Domain-Specific Language (DSL) file with a `.shl` extension.
The editor features a live preview panel that shows you the generated DSL code as you make changes. It also includes functionalities for defining rules and scenes, and validating the generated DSL against a grammar.

## How to Run the Program

If you want to run the program, clone the repository to your machine, and run the following command:

`python main.py`

That command will open the application.

## Technologies Used

- **Python**: The core programming language.
- **Tkinter**: Python's standard GUI (Graphical User Interface) toolkit, used for building the application's interface.
- **textX**: A meta-language for building Domain-Specific Languages (DSLs) in Python, used for defining and validating the SmartHome DSL grammar.
- **Standard Python Libraries**: `os` for operating system interactions (e.g., file paths) and `re` for regular expressions (used in DSL parsing).

## Features

### Managing Locations

- **Add Location**: Click the "Add Location" button. You will be prompted to enter a name. Note that any spaces in the name will be automatically removed (e.g., "Living Room" becomes "LivingRoom").
- **Remove Location**: Select a location from the list and click "Remove Location".

### Managing Devices

You can add devices to any location you've created, view all devices, and edit their properties.

- **Add Device**: Click the "Add Device" button. A new window will appear where you can:
  1.  Select the device type (e.g., Light, Sensor, AC).
  2.  Enter a name for the device.
  3.  Assign it to an existing location from a dropdown menu.
- **Remove Device**: This functionality allows you to remove the last added device from a selected location.
- **See All Devices**: Opens a dialog showing all devices across all locations. From this dialog, you can select a device and click "Edit Device" to modify its name, type, or assigned location.

### Managing Rules

Rules define automated behaviors based on certain conditions.

- **Add Rule**: Click the "Add Rule" button. A dialog will appear where you can:
  1.  Provide a name for the rule.
  2.  Define a condition based on detector devices (e.g., a Thermostat detecting a certain temperature, or a Sensor/Camera detecting an event).
  3.  Specify one or more actions to be performed when the condition is met, involving other devices and their functionalities.

### Managing Scenes

Scenes allow you to group multiple actions together to be triggered manually or as part of a rule.

- **Add Scene**: Click the "Add Scene" button. A dialog will appear where you can:
  1.  Provide a name for the scene.
  2.  Associate the scene with a specific location.
  3.  Define a sequence of actions involving various devices and their functionalities.

## DSL Preview

The panel on the right side of the window provides a real-time preview of the `.shl` file's content. As you add, remove, or modify locations and devices, this preview will update automatically to reflect the state of your configuration.

## File Management

- **Create New File**: Starts a new SmartHome configuration, prompting you to save a new `.shl` file.
- **Save file**: Saves the current configuration to the opened `.shl` file.
- **Save As...**: Allows you to save the current configuration to a new `.shl` file.
- **Open...**: Closes the current configuration and opens a different `.shl` file.

## Validation

- **Validate and Start SmartHome**: This button takes the current DSL code from the preview, validates it against the defined `grammar.tx` using `textX`, and provides feedback on whether the program is syntactically correct. If valid, it simulates starting the SmartHome program.

## Current Limitations and Future Improvements

While the editor provides core functionalities, there are some areas for improvement:

- **Rules and Scenes Editing/Deletion**: Currently, there is no direct functionality to edit or delete existing rules and scenes through the GUI. They can only be added.
- **Device Removal**: The "Remove Device" button currently removes the _last_ device added to a selected location, rather than allowing the user to select a specific device for removal.
- **Device Name Uniqueness**: When adding devices, there is no check to prevent duplicate device names within the same location.
- **Error Handling in DSL Parsing**: The DSL parser is robust for valid syntax but could offer more specific error messages for common user mistakes.
- **Advanced Rule/Scene Logic**: The current implementation of rules and scenes is basic; future versions could include more complex conditional logic, time-based triggers, and nested actions.
