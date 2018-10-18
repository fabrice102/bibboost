.PHONY: all clean mrproper test FORCE

PYTHON3=python3

all: build/bibboost.pyz

build/bibboost.pyz: build/venv/bin/activate requirements.txt $(wildcard bibboost/*) $(wildcard bibboost/**/*)
	mkdir -p build/bibboost
	cp -R bibboost build/bibboost/bibboost
	
	set -e; \
	source build/venv/bin/activate; \
	cd build; \
	python3 -m pip install -r ../requirements.txt -t bibboost; \
	python3 -m zipapp bibboost -m "bibboost.__main__:main" -p "/usr/bin/env python3" -c

build/venv/bin/activate:
	mkdir -p build
	$(PYTHON3) -m venv build/venv
	
	set -e; \
	source build/venv/bin/activate; \
	python3 -m pip install --upgrade pip

test:
	cd test && $(MAKE) test

clean:
	cd test && $(MAKE) clean
	rm -rf build/venv
	rm -rf build/bibboost

mrproper: clean
	rm -rf build

