.ONESHELL:
SHELL=bash

PREFIX:=/usr/local

UNRAR_FILE=unrarsrc-7.2.2.tar.gz
UNRAR_URL=https://www.rarlab.com/rar/$(UNRAR_FILE)

VENV_INSTALL_PATH=$(PREFIX)/share/gamma-launcher-venv

all: unrar/libunrar.so

$(UNRAR_FILE):
	wget -O $@ $(UNRAR_URL)

unrar: $(UNRAR_FILE)
	tar xf $<

unrar/libunrar.so: unrar
	+make -C unrar lib

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

.PHONY: uninstall
uninstall:
	rm -rf $(DESTDIR)$(PREFIX)/bin/gamma-launcher $(DESTDIR)$(VENV_INSTALL_PATH)

.PHONY: clean
clean:
	rm -rf unrar/ $(UNRAR_FILE) ../build ../gamma_launcher.egg-info
