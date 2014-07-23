OS := $(shell uname -s)

ifdef CI
	BLENDER := $(BLENDER_BIN)
else ifeq ($(OS),Linux)
	# TODO(SK): Linux blender executable filepath missing
	BLENDER :=
else ifeq ($(OS),Darwin)
	BLENDER := /Applications/Blender/blender.app/Contents/MacOS/blender
endif

SOURCE_DIRECTORY := ./pam
BLENDERFLAGS     := --background --disable-crash-handler -noaudio
TEST_DIRECTORY   := $(SOURCE_DIRECTORY)/tests
TEST_ENTRY       := run_tests.py
FAILED_STRING    := FAILED
DOCS_DIR         := ./docs
DOCS_ENTRY       := $(DOCS_DIR)/blender_sphinx.py
BLENDFILE        := test_universal.blend
LOGFILE          := unittest.log
PEP8_FLAGS       := --ignore=E501 --show-source

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  test  to run all tests"
	@echo "  clean to clean up temporary files"
	@echo "  pep8  to check pep8 compliance"
	@echo "  docs  to generate documentation"

test: clean pep8 binary-exists
	@echo "Running unittests"
	$(BLENDER) $(TEST_DIRECTORY)/$(BLENDFILE) $(BLENDERFLAGS) --python $(TEST_ENTRY)

test-ci: clean pep8 binary-exists
	@echo "Running continuous integration unittests"
	$(BLENDER) $(TEST_DIRECTORY)/$(BLENDFILE) $(BLENDERFLAGS) --python $(TEST_ENTRY) 2>&1 | tee $(LOGFILE)
	@if grep -q $(FAILED_STRING) $(LOGFILE); then exit 1; fi

binary-exists:
	@if [ -z $(BLENDER) ]; then echo "Blender binary path not set"; exit 1; fi
	@if [ ! -x $(BLENDER) ]; then echo "Blender binary is missing or it is not executable"; exit 1; fi

clean:
	@echo "Cleaning logfiles"
	rm -rf $(LOGFILE)
	@echo "Cleaning cached python files"
	find . \( -name "__pycache__" -o -name "*.pyc" \) -delete
	@echo "Cleaning documentation files"
	rm -rf $(DOCS_DIR)/_build/*

pep8:
	@echo "Checking pep8 compliance"
	pep8 $(SOURCE_DIRECTORY) $(PEP8_FLAGS)

docs: binary-exists
	@echo "Generating html documentation"
	$(BLENDER) $(BLENDERFLAGS) --python $(DOCS_ENTRY)

.PHONY: help clean docs test test-ci check-binary
