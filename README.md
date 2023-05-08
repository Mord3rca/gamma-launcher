# GAMMA Launcher

Starting G.A.M.M.A. .NET Launcher is not possible on GNU/Linux because of .NET / powershell scripts

This is a reimplementation of G.AM.M.A. launcher used for the first setup. You will need to follow
[DravenusRex's guide](https://github.com/DravenusRex/stalker-gamma-linux-guide) to have a working game.

## Installation

It's strongly advised to install this in a [venv](https://docs.python.org/3/library/venv.html#creating-virtual-environments) (Python Virtual Environment)

A quick guide on how to do this is to open your terminal/command prompt and navigating to the downloaded folder containing gamma-launcher, and typing `python3 -m venv env` on Linux, or `py -m venv env` on Windows.

You will then have to enter the virtual environment by typing `source env/bin/activate` on Linux, or `.\env\Scripts\activate` on Windows.

To confirm that you're in the right place, type `which python` on Linux, or `where python` on Windows. It should print out either `.../env/bin/python` or `...\env\Scripts\python.exe`, respectively.

You may first have to upgrade pip for the installation to work. (If it's complaining about a 'bad interpreter', for example.) If this is the case, type `pip install --upgrade pip`.

If currently in your gamma-launcher folder, you can simply type `pip install .` OR `pip install directory`. Replace 'directory' with the actual path of said directory. The specificed directory must contain the gamma-launcher setup.py file.

If all went well, you can now use the `gamma-launcher` command as intended.

(Type `deactivate` to leave the virtual environment. Use the previous `source` command to re-enter it.)

## Commands

### Check MD5

This will perform a MD5 check for all ModDB addons

To run it: `gamma-launcher check-md5 --gamma <GAMMA path>`

### Full Install

This will install all mods based on [Stalker_GAMMA](https://github.com/Grokitach/Stalker_GAMMA)

To setup your GAMMA folder:  `gamma-launcher full-install --anomaly <Anomaly path> --gamma <GAMMA path>`

Afterwards, you will need to start Mod Organizer and set Anomaly Path (launcher can't do that ... yet.)

### Remove ReShade

This will do remove ReShade based on [this guide](https://reshade.me/forum/general-discussion/4398-howto-uninstall-reshade)

To use it: `gamma-launcher remove-reshade --anomaly <Anomaly path>`

### Purge Shader Cache

This will delete cached shaders

To use it: `gamma-launcher purge-shader-cache --anomaly <Anomaly path>`

### Test Mod Maker

This command will verify if additonal installation directives are valid
(aka folder is in the archive)

To use it: `gamma-launcher test-mod-maker --gamma <GAMMA path>`

## Troubleshoot

### Shader compilation error

Remove ReShade with: `gamma-launcher remove-reshade --anomaly <Anomaly path>`

Also remove some shaders mods:
* 188- Enhanced Shaders - KennShade
* 189- Beef's NVG - theRealBeef
* 190- Screen Space Shaders - Ascii1457
* 290- Atmospherics Shaders Weathers and Reshade - Hippobot


### Something else ?

Well .... you're alone kid. Good luck. Try downgrading DirectX version or looking at log file.

## Contributing

You can do a PR but make sure you respect `flake8` coding style.

Also, avoid OS specific code. I plan to build it with pyinstaller for Windows users.

## Disclaimer

I did not have access to the official launcher so, I can only guess how it's done.

Miraculously, it works on my side. Feel free to contribute if something is wrong.
