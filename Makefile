OS := $(shell uname -s)

ifdef CI
	BLENDER := $(BLENDER_BIN)
else ifeq ($(OS),Linux)
	# TODO(SK): Linux blender executable filepath missing
	BLENDER :=
else ifeq ($(OS),Darwin)
	BLENDER := /Applications/Blender/blender.app/Contents/MacOS/blender
endif

# Flags
BLENDERFLAGS := --background --disable-crash-handler -noaudio
PEP8FLAGS    := --ignore=E501 --show-source
PYLINTFLAGS  := --disable=C0301,C0103 --msg-template='{msg_id}:{line:3d},{column}: {obj}: {msg}'

# Base
DIR_SOURCE := ./pam

# Unittest
DIR_TEST    := ./tests
SCRIPT_TEST := run_tests.py
TEST_FAILED := FAILED
TEST_BLEND  := test_universal.blend
LOGFILE     := unittest.log

# Documentation
DIR_DOC    := ./docs
SCRIPT_DOC := ./build_docs.py


default: help

all: clean pep8 pylint tests docs


help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean  to clean"
	@echo "  tests   to run tests"
	@echo "  pep8   to check pep8 compliance"
	@echo "  pylint to run pylint"
	@echo "  docs    to build documentation"

tests: binary-exists clean
	@echo "Running unittests"
	$(BLENDER) $(DIR_TEST)/$(TEST_BLEND) $(BLENDERFLAGS) --python $(SCRIPT_TEST)

tests-ci: binary-exists clean
	@echo "Running continuous integration unittests"
	$(BLENDER) $(DIR_TEST)/$(TEST_BLEND) $(BLENDERFLAGS) --python $(SCRIPT_TEST) 2>&1 | tee $(LOGFILE)
	@if grep -q $(TEST_FAILED) $(LOGFILE); then exit 1; fi

clean:
	@echo "Cleaning log files"
	@rm -rf $(LOGFILE)
	@echo "Cleaning cached python files"
	@find . \( -name "__pycache__" -o -name "*.pyc" \) -delete
	@echo "Cleaning documentation directory"
	@rm -rf $(DIR_DOC)/_build/

pep8: clean
	@echo "Checking pep8 compliance"
	pep8 $(DIR_SOURCE) $(PEP8FLAGS)

pylint: binary-exists clean
	@echo "Running pylint"
	pylint $(DIR_SOURCE) $(PYLINTFLAGS)

docs: binary-exists clean
	@echo "Generating documentation"
	$(BLENDER) $(BLENDERFLAGS) --python $(SCRIPT_DOC)

binary-exists:
	@if [ -z $(BLENDER) ]; then echo "Blender binary path not set"; exit 1; fi
	@if [ ! -x $(BLENDER) ]; then echo "Blender binary is missing or it is not executable"; exit 1; fi

.PHONY: help clean docs tests tests-ci check-binary
