# SmartHome DSL Editor

## Overview

The SmartHome DSL Editor is a graphical user interface (GUI) application built with Python and Tkinter that allows you to create and manage configurations for a smart home system. It provides a user-friendly way to define places, locations, and devices, which are then saved into a custom Domain-Specific Language (DSL) file with a `.shl` extension.

The editor features a live preview panel that shows you the generated DSL code as you make changes.

## How to Run the Program

To run the application, you need Python 3 installed on your system.

1.  Navigate to the root directory of the project (`smarthome`).
2.  Run the main application file:

    ```bash
    python main.py
    ```

## Getting Started

When you first launch the application, you will be prompted to either create a new "Place" or open an existing one.

- **Creating a new Place** will ask you to save a new `.shl` file. This file will store all your smart home configurations.
- **Opening an existing Place** will allow you to load a previously saved `.shl` file to continue editing.

The application works exclusively with `.shl` (SmartHome Language) files.

## Features

### Managing Locations

Locations are distinct areas within your home, like "LivingRoom" or "Bedroom".

- **Add Location**: Click the "Add Location" button. You will be prompted to enter a name. Note that any spaces in the name will be automatically removed (e.g., "Living Room" becomes "LivingRoom").
- **Remove Location**: Select a location from the list and click "Remove Location".

### Managing Devices

You can add devices to any location you've created.

- **Add Device**: Click the "Add Device" button. A new window will appear where you can:
  1.  Select the device type (e.g., Light, Sensor, AC).
  2.  Enter a name for the device.
  3.  Assign it to an existing location from a dropdown menu.

### Rules and Scenes (Work in Progress)

The functionality for adding and managing **Rules** and **Scenes** is currently under development. While the buttons are visible in the UI, they have limited functionality and are intended as placeholders for future implementation.

## DSL Preview

The panel on the right side of the window provides a real-time preview of the `.shl` file's content. As you add, remove, or modify locations and devices, this preview will update automatically to reflect the state of your configuration.

## File Management

- **Save file**: Saves the current configuration to the opened `.shl` file.
- **Save As...**: Allows you to save the current configuration to a new `.shl` file.
- **Open...**: Closes the current configuration and opens a different `.shl` file.
