# Easy Install

Avoid Linux distro dependencies issue and install gamma-launcher easily

## Requirement

The following programs a required to run this script:

* C & C++ toolchain
* make
* wget

If you are on Debian/Ubuntu, your can use `apt install build-essential git python3-venv wget` to install every requirement in one go.

## System-wide installation

This will compile & install everything to run `gamma-launcher` in */usr/local*

```sh
$ make -j$(nproc)
$ sudo make install
```

## User installation

To install `gamma-launcher` without root privilege use:
```sh
$ make -j$(nproc)
$ make PREFIX="${HOME}/.local" install
```

You will be able to run `gamma-launcher` by calling *${HOME}/.local/bin/gamma-launcher*
