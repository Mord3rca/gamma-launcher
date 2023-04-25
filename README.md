# GAMMA Launcher

Starting G.A.M.M.A. .NET Launcher is not possible on GNU/Linux because of .NET / powershell scripts

This is a reimplementation of G.AM.M.A. used for the first setup (only mod supported for now)

You will need to follow [DravenusRex's guide](https://github.com/DravenusRex/stalker-gamma-linux-guide) and skip the Windows VM setup
since you won't have to run Grok's GAMMA Installer


## Installation

To install the launcher, use *pip* command follow: `pip install <directory>`

Where *directory* is the toplevel directory containing `setup.py`

## Usage

Once installed, you can use: `gamma-launcher full_install --anomaly <Anomaly path> --gamma <GAMMA path>`
to setup your GAMMA mods folder.

Afterwards, you will need to start Mod Organizer and set Anomaly Path (launcher can't do that ... yet.)

Remove some mods:
* 188- Enhanced Shaders - KennShade
* 189- Beef's NVG - theRealBeef
* 190- Screen Space Shaders - Ascii1457
* 290- Atmospherics Shaders Weathers and Reshade - Hippobot

Also, remove ReShade with: `gamma-launcher remove_reshade --anomaly <Anomaly path>`


## Troubleshoot

Well .... you're alone kid. Good luck. Try downgrading DirectX version or looking at log file.
