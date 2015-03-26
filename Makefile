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
SOURCE_DIRECTORY := ./pam

# Unittest
TEST_DIRECTORY := ./tests
TEST_FAILED    := FAILED
TEST_LOG       := $(TEST_DIRECTORY)/test.log

# Documentation
DOC_DIRECTORY := ./docs
DOC_SCRIPT    := ./build_docs.py

TESTCASES=$(patsubst %_test.py,%,$(notdir $(wildcard $(TEST_DIRECTORY)/*_test.py)))


default: help

all: clean pep8 tests docs

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean  to clean"
	@echo "  tests  to run tests"
	@echo "  pep8   to check pep8 compliance"
	@echo "  pylint to run pylint"
	@echo "  docs   to build documentation"

tests: $(TESTCASES)

$(TESTCASES): binary-exists clean
	$(BLENDER) $(TEST_DIRECTORY)/$@_test.blend $(BLENDERFLAGS) --python $(TEST_DIRECTORY)/$@_test.py | tee $(TEST_LOG)
	@if grep -q $(TEST_FAILED) $(TEST_LOG); then rm -f $(TEST_LOG); exit 1; fi

clean:
	@echo "Cleaning log files"
	@rm -f $(TEST_LOG)
	@echo "Cleaning cached python files"
	@find . \( -name "__pycache__" -o -name "*.pyc" \) -delete
	@echo "Cleaning documentation directory"
	@rm -rf $(DOC_DIRECTORY)/_build/

pep8: clean
	@echo "Checking pep8 compliance"
	@pep8 $(SOURCE_DIRECTORY) $(PEP8FLAGS)

pylint: binary-exists clean
	@echo "Running pylint"
	@pylint $(SOURCE_DIRECTORY) $(PYLINTFLAGS)

docs: binary-exists clean
	@echo "Generating documentation"
	@$(BLENDER) $(BLENDERFLAGS) --python $(DOC_SCRIPT)

binary-exists:
	@if [ -z $(BLENDER) ]; then echo "Blender binary path not set"; exit 1; fi
	@if [ ! -x $(BLENDER) ]; then echo "Blender binary is missing or it is not executable"; exit 1; fi

.PHONY: help clean docs tests check-binary
