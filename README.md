# GAMMA Launcher

Starting G.A.M.M.A. .NET Launcher is not possible on GNU/Linux because of .NET / powershell scripts

This is a reimplementation of G.AM.M.A. launcher used for the first setup. You will need to follow
[DravenusRex's guide](https://github.com/DravenusRex/stalker-gamma-linux-guide) to have a working game.

## Installation

### Using release

By downloading gamma-launcher from the [latest release](https://github.com/Mord3rca/gamma-launcher/releases/latest), you can use it without any installation. Everything is self contained in an executable. Release built with Ubuntu.

Use the `--cache-directory` option to re-use previously downloaded files.

### Using pip (from source)

It's strongly advised to install this in a [venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment) (Python Virtual Environment)

A quick guide on how to do this is to open your terminal/command prompt and navigating to the downloaded folder containing gamma-launcher, and typing `python3 -m venv env` on Linux, or `py -m venv env` on Windows.

You will then have to enter the virtual environment by typing `source env/bin/activate` on Linux, or `.\env\Scripts\activate` on Windows.

To confirm that you're in the right place, type `which python` on Linux, or `where python` on Windows. It should print out either `.../env/bin/python` or `...\env\Scripts\python.exe`, respectively.

You may first have to upgrade pip for the installation to work. (If it's complaining about a 'bad interpreter', for example.) If this is the case, type `pip install --upgrade pip`.

If currently in your gamma-launcher folder, you can simply type `pip install .` OR `pip install directory`. Replace 'directory' with the actual path of said directory. The specificed directory must contain the gamma-launcher setup.py file.

If all went well, you can now use the `gamma-launcher` command as intended.

(Type `deactivate` to leave the virtual environment. Use the previous `source` command to re-enter it.)

## Commands

### Anomaly Install

Create an usable Anomaly installation is target directory

To setup Anomaly:  `gamma-launcher anomaly-install --anomaly <Anomaly path>`

### Check Anomaly

Verify Anomaly installation with:  `gamma-launcher check-anomaly --anomaly <Anomaly path>`

### Check MD5

This will perform a MD5 check for all ModDB addons

To run it: `gamma-launcher check-md5 --gamma <GAMMA path>`

### Full Install / Update

This will install/update all mods based on [Stalker_GAMMA](https://github.com/Grokitach/Stalker_GAMMA)

To setup/update your GAMMA folder:  `gamma-launcher full-install --anomaly <Anomaly path> --gamma <GAMMA path>`

Afterwards, you will need to start Mod Organizer and set Anomaly Path (launcher can't do that ... yet.)

### Remove ReShade

This will do remove ReShade based on [this guide](https://reshade.me/forum/general-discussion/4398-howto-uninstall-reshade)

To use it: `gamma-launcher remove-reshade --anomaly <Anomaly path>`

### Purge Shader Cache

This will delete cached shaders

To use it: `gamma-launcher purge-shader-cache --anomaly <Anomaly path>`

### USVFS Workaround

This will create a usable GAMMA installation without ModOrganizer.

DO NOT USE IT if wine is compatible with ModOrganizer, this will remove all mods flexibility.

To use it: `gamma-launcher usvfs-workaround --anomaly <Anomaly path> --gamma <GAMMA path> --final <Final Install path>`

### Test Mod Maker

This command will verify if additonal installation directives are valid
(aka folder is in the archive)

To use it: `gamma-launcher test-mod-maker --gamma <GAMMA path>`

## Troubleshoot

### Glibc Errors

Install gamma launcher in a [venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment). See the *Using pip (from source)* section above.

### Magic Errors

Try prepending `MAGIC=/usr/share/file/misc/magic` or `LD_PRELOAD=/usr/lib/libmagic.so` to the `./gamma-launcher` command.

Otherwise, attempt to run in a [venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment).

### Shader compilation error

Remove ReShade with: `gamma-launcher remove-reshade --anomaly <Anomaly path>`

Also remove some shaders mods:
* 188- Enhanced Shaders - KennShade
* 189- Beef's NVG - theRealBeef
* 190- Screen Space Shaders - Ascii1457
* 290- Atmospherics Shaders Weathers and Reshade - Hippobot

### ModuleNotFoundError: No module named 'distutils'

The `distutils` module is required to install Python packages but it was removed in Python 3.12. You can still use it by installing `setuptools` (inside the venv): `pip install setuptools`

### rarfile.RarCannotExec: Cannot find working tool

You are missing a tool that extracts RAR files. You can use something like `unrar` on Linux. To install it run the following command:
- On Ubuntu: `sudo apt install unrar`
- On Fedora **(RPM Fusion required)**: `sudo dnf install unrar`. Note that before the installation you will need to enable the **non-free** RPM Fusion repository since the default package provided by Fedora will cause problems. [Instructions on how to enable it here](https://rpmfusion.org/Configuration).

### Something else ?

Well .... you're alone kid. Good luck. Try downgrading DirectX version or looking at log file.

## Contributing

You can do a PR but make sure you respect `flake8` coding style.

Also, avoid OS specific code. I plan to build it with pyinstaller for Windows users.

## Disclaimer

I did not have access to the official launcher so, I can only guess how it's done.

Miraculously, it works on my side. Feel free to contribute if something is wrong.
