# Have docker installed and configured correctly (i.e. your user in the docker group)
# Run the following commands:
# mkdir -p artifacts
# docker run --user $UID:$GID -v ./artifacts:/artifacts --rm -it $(docker build -q .)
# ./artifacts/gamma-installer

# Use the latest Debian stale
FROM debian:trixie

# Set debconf to run non-interactively
ARG DEBIAN_FRONTEND=noninteractive

# Add contrib for unrar
RUN sed -i /etc/apt/sources.list.d/debian.sources -e 's/Components: main/Components: main contrib non-free/g'

RUN apt update && apt -y upgrade && apt -y --no-install-recommends install \
	binutils \
	libunrar-dev \
	pyinstaller \
	python3-bs4 \
	python3-cffi \
	python3-charset-normalizer \
	python3-cloudscraper \
	python3-pycryptodome \
	python3-dev \
	python3-git \
	python3-pyparsing \
	python3-pip \
	python3-platformdirs \
	python3-pyinstaller \
	python3-pyppmd \
	python3-py7zr \
	python3-rarfile \
	python3-requests \
	python3-setuptools \
	python3-soupsieve \
	python3-tenacity \
	python3-tqdm \
	&& rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1

RUN mkdir /work

ADD launcher /work/launcher

ADD pyproject.toml /work

WORKDIR /work

# pyinstaller in Debian trixie is 6.13, which has a bug that prevents things from working.
# We install the latest as of this writing, 6.17.0
RUN pip install --break-system-packages pyinstaller

RUN pip install --break-system-packages .

RUN pyinstaller \
	--onefile \
	--noconfirm \
	--add-binary=/usr/lib/x86_64-linux-gnu/libunrar.so:. \
	$(command -v gamma-launcher)

CMD ["cp", "-a", "dist/gamma-launcher", "/artifacts"]
