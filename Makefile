prefix = /usr
PYTHON ?= python3

servicedir = ${prefix}/lib/obs/service

all: build

build:
	echo '#!/usr/bin/python3' > obs_scm_bridge.py
	cat obs_scm_bridge/manifest.py >> obs_scm_bridge.py
	echo '' >> obs_scm_bridge.py
	cat obs_scm_bridge/__main__.py >> obs_scm_bridge.py
	chmod +x obs_scm_bridge.py

clean:
	find -name "*.pyc" -exec rm {} \;
	find -name '*.pyo' -exec rm {} \;
	rm -f obs_scm_bridge.py

.PHONY: all build clean
