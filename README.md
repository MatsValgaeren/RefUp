# RefUp (Maya Reference Version Manager)

*A tool to (auto) update references in your Maya file.*

*Watch Here: [YouTube Video](https://youtu.be/Bs3TtzVg9mM)!*


[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Features

- Directory Scan: Choose a directory and automatically scan for all available versions of referenced assets in your Maya scene.
- Reference Version Selection: See versions of each reference and select which version to use for every reference in your scene.
- Auto-Update: Enable auto-update for specific references to always use the latest available version on scene startup.

## Installation

1. Download or clone this repository.
2. Copy the RefUp and userSetup script file to your Maya scripts directory:
   (If you already have a userSetup script then you need to combine these two yourself.)
```
Documents/maya/<version>/scripts/
```
4. Copy the settings.json file in (you need to make the folder yourself):
```
Documents/maya/<version>/prefs/RefUp
```
3. In Maya, open the Script Editor and run:
```
import RefUp
RefUp.show_ui()
```


## Usage

![RefUp_ui_002_v001 png](https://github.com/user-attachments/assets/6fedf1d7-4bd8-4e76-ac7b-167d5aaef8d8)
![RefUp_ui_001_v001](https://github.com/user-attachments/assets/eabfb695-5cff-494d-be91-a5e0cd9aab59)


1. **Run the RefUp in Maya** to open the UI.
2. **Select your working directory** containing referenced assets in the settings tab.
3. **Click "Update Settings"** to apply changes.
4. **Chose the version of all your references** in your scene.
5. **Click "Update References"** to apply changes.
6. (Optional) Select files you want auto update on start-up in the settings tab.


**Watch the Demo here:** [YouTube Video](https://youtu.be/Bs3TtzVg9mM)!


## Requirements

- Autodesk Maya (version 2025+)

## Credits

- Script by Mats Valgaeren

## License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0)
