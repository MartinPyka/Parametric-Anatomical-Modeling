OS := $(shell uname -s)

ifdef CI
	BLENDER := $(BLENDER_BIN)
else ifeq ($(OS),Linux)
	# TODO(SK): Linux blender executable filepath missing
	BLENDER :=
else ifeq ($(OS),Darwin)
	BLENDER := /Applications/Blender/blender.app/Contents/MacOS/blender
endif

BLENDERFLAGS     := --background --disable-crash-handler -noaudio
PEP8FLAGS       := --ignore=E501 --show-source

DIR_SOURCE	 := ./pam
DIR_TEST         := $(DIR_SOURCE)/tests
DIR_DOC          := ./docs
SCRIPT_TEST      := run_tests.py
SCRIPT_DOC       := $(DIR_DOC)/blender_sphinx.py
TEST_FAILED      := FAILED
TEST_BLEND       := test_universal.blend

LOGFILE          := unittest.log

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  test  to run all tests"
	@echo "  clean to clean up temporary files"
	@echo "  pep8  to check pep8 compliance"
	@echo "  docs  to generate documentation"

test: clean pep8 binary-exists
	@echo "Running unittests"
	$(BLENDER) $(DIR_TEST)/$(TEST_BLEND) $(BLENDERFLAGS) --python $(SCRIPT_TEST)

test-ci: clean pep8 binary-exists
	@echo "Running continuous integration unittests"
	$(BLENDER) $(DIR_TEST)/$(TEST_BLEND) $(BLENDERFLAGS) --python $(SCRIPT_TEST) 2>&1 | tee $(LOGFILE)
	@if grep -q $(TEST_FAILED) $(LOGFILE); then exit 1; fi

binary-exists:
	@if [ -z $(BLENDER) ]; then echo "Blender binary path not set"; exit 1; fi
	@if [ ! -x $(BLENDER) ]; then echo "Blender binary is missing or it is not executable"; exit 1; fi

clean:
	@echo "Cleaning logfiles"
	rm -rf $(LOGFILE)
	@echo "Cleaning cached python files"
	find . \( -name "__pycache__" -o -name "*.pyc" \) -delete
	@echo "Cleaning documentation files"
	rm -rf $(DIR_DOC)/_build/*

pep8:
	@echo "Checking pep8 compliance"
	pep8 $(DIR_SOURCE) $(PEP8FLAGS)

docs: binary-exists
	@echo "Generating html documentation"
	$(BLENDER) $(BLENDERFLAGS) --python $(SCRIPT_DOC)

.PHONY: help clean docs test test-ci check-binary
