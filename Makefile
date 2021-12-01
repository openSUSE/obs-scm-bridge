prefix = /usr
PYTHON ?= python

serverdir = ${prefix}/lib/obs/server

all:

install:
	install -d $(DESTDIR)$(serverdir)
	install -m 0755 download_assets obs-scm $(DESTDIR)$(serverdir)
	install -m 0644 helpers.py $(DESTDIR)$(serverdir)

test:
	flake8 set_version tests/
	${PYTHON} -m unittest discover tests/

clean:
	find -name "*.pyc" -exec rm {} \;
	find -name '*.pyo' -exec rm {} \;
	rm -rf set_versionc

.PHONY: all install test
