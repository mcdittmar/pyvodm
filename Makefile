pypkg = pyvodm

build:
	@echo "Build python package - ${pypkg}"
	python setup.py build

clean:
	@echo "Clean python package - ${pypkg}"
	rm -rf ./${pypkg}.egg-info
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./pyvodm/__pycache__
	rm -rf ./pyvodm/utils/__pycache__
	rm -rf ./pyvodm/document/writers/__pycache__
	rm -rf ./pyvodm/document/__pycache__
	rm -rf ./pyvodm/modelMap/__pycache__
	rm -rf ./pyvodm/model/builders/__pycache__
	rm -rf ./pyvodm/model/__pycache__

	@echo "Clean test space"
	rm -rf ./tests/bin/__pycache__
	rm -rf ./tests/out

install:
	python setup.py install

uninstall:
	python -m pip uninstall -y "pyvodm"

test:
	@echo "Test ${pypkg} python package" 
	python -m unittest tests/bin/unittest_params.py
	python -m unittest tests/bin/unittest_document.py
	python -m unittest tests/bin/unittest_model.py
	python -m unittest tests/bin/unittest_modelmap.py
	python -m unittest tests/bin/unittest_docbuilder.py

all: build test install
