.ONESHELL:
SHELL=bash

PREFIX:=/usr/local

UNRAR_FILE=unrarsrc-7.2.2.tar.gz
UNRAR_URL=https://www.rarlab.com/rar/$(UNRAR_FILE)

7ZZ_FILE=7z2501-src.tar.xz
7ZZ_URL=https://7-zip.org/a/$(7ZZ_FILE)

VENV_INSTALL_PATH=$(PREFIX)/share/gamma-launcher-venv

all: unrar/libunrar.so 7zsrc/CPP/7zip/Bundles/Alone/_o/7za

# libunrar.so compilation
$(UNRAR_FILE):
	wget -O $@ $(UNRAR_URL)

unrar: $(UNRAR_FILE)
	tar xf $<

unrar/libunrar.so: unrar
	+make -C unrar lib

# 7zz compilation
$(7ZZ_FILE):
	wget -O $@ $(7ZZ_URL)

7zsrc/CPP/7zip/Bundles/Alone/_o/7za: $(7ZZ_FILE)
	mkdir -p 7zsrc
	tar xf $< -C 7zsrc
	+make -C 7zsrc/CPP/7zip/Bundles/Alone/ -f makefile.gcc

.PHONY: install-venv install
install-venv:
	if [ ! -d $(DESTDIR)$(VENV_INSTALL_PATH) ]; then
		python3 -m venv "$(VENV_INSTALL_PATH)"
	fi
	source "$(DESTDIR)$(PREFIX)/share/gamma-launcher-venv/bin/activate"
	pip install --upgrade pip
	pip install ..

install: install-venv
	install -D gamma-launcher $(DESTDIR)$(PREFIX)/bin/gamma-launcher

	install -D unrar/libunrar.so "$(DESTDIR)$(VENV_INSTALL_PATH)/lib/libunrar.so"

	install -D 7zsrc/CPP/7zip/Bundles/Alone/_o/7za "$(DESTDIR)$(VENV_INSTALL_PATH)/bin/7za"
	ln -sf 7za "$(DESTDIR)$(VENV_INSTALL_PATH)/bin/7z"

.PHONY: uninstall
uninstall:
	rm -rf $(DESTDIR)$(PREFIX)/bin/{7z,7za,gamma-launcher} $(DESTDIR)$(VENV_INSTALL_PATH)

.PHONY: clean
clean:
	rm -rf 7zsrc/ unrar/ $(UNRAR_FILE) ../build ../gamma_launcher.egg-info
