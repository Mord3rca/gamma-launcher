# Contributing

Feel free to contribute to this project by creating a pull request or an issue.

However, some listed subject here are not welcome...

## Packaging

Adding a new packaging system should be avoided, 
the only packaging maintained by this project are:

* pip installation
* pyinstaller
* easy-install

If you want to add your own, fork this repo and add it. The only thing you will be allowed
to merge to this is a reference in README.md to point to your new packaging system (ex: AUR packaging).

In any case, no issues / PR related to your installation method will be accepted here.

## Libunrar

Yes, **libunrar** can be a pain for some like Suse etc but for now, it's the best choice to work on most
distro.

If you distro do not distribute it, use *easy-install* to install gamma-launcher in parallel of `7z` & *libunrar*

### But why not python-unrar ?

Slow as fuck. Will decompress each file one by one ... making a `fork()` for each one.
See [#127 (comment)](https://github.com/Mord3rca/gamma-launcher/issues/127#issuecomment-2197656991)

### And why not 7z for all type of archive ?

Yeah ... It may work on your distro, but you are not alone.
See [#240 (comment)](https://github.com/Mord3rca/gamma-launcher/pull/240#issuecomment-3482497749)
