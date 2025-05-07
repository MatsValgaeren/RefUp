# RefUp

[![Build Status](https://img.shields.io/github/actions/workflow/status/username/repo/ci.yml?branch=main)](https://github.com/MatsValgaeren/FrameForge/actions)
[![Coverage](https://img.shields.io/codecov/c/github/username/repo)](https://codecov.io/gh/username/repo)
[![Latest Release](https://img.shields.io/github/v/release/username/repo)](https://github.com/MatsValgaeren/FrameForge/releases)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Issues](https://img.shields.io/github/issues/username/repo)](https://github.com/MatsValgaeren/FrameForge/issues)

</div>

<details>
<summary>Table of Contents</summary>

- [About](#about)
- [Features](#features)
- [Installation](#installation)
  - [Requirements](#requirements)
  - [Maya Scipt Setup](#maya-scipt-setup)
- [Usage](#usage)
- [Roadmap & Contributing](#roadmap--contributing)
- [Credits](#credits)
- [License](#license)

</details>


## About

A tool to (auto) update references in your Maya file.

*Watch Demo Video Here: [YouTube Video](https://youtu.be/Bs3TtzVg9mM)*


## Features

- Scan a directory for all available versions of referenced assets in your Maya scene
- View and select versions for each reference in your scene
- Enable auto-update for specific references to always use the latest version on scene startup


## Installation

#### Requirements

-   Autodesk Maya (version 2025+)

#### Maya Scipt Setup

1.  Download or clone this repository.
2.  Copy the RefUp and userSetup script file to your Maya scripts directory:
   (If you already have a userSetup script then you need to combine these two yourself.)
```
Documents/maya/<version>/scripts/
```
2.  Copy the settings.json file in (you need to make the folder yourself):
```
Documents/maya/<version>/prefs/RefUp
```
3.  In Maya, open the Script Editor and run:
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

***Watch the Demo here: [YouTube Video](https://youtu.be/SPfN98WdyZ4)***


## Roadmap & Contributing

See the [open issues](https://github.com/MatsValgaeren/FrameForge/issues) to track planned features, known bugs, and ongoing work.

If you encounter any bugs or have feature requests, please submit them as new issues there.  Your feedback and contributions help improve RefUp!


## Credits

-   Script by Mats Valgaeren
-   Powered by:
    -   [PyQt6](https://pypi.org/project/PyQt6/)


## License

[GNU General Public License v3.0](LICENSE)
