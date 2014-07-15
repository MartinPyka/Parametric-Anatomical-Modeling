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

TEST_DIRECTORY := $(SOURCE_DIRECTORY)/tests
TEST_FLAGS := --background --disable-crash-handler -noaudio
TEST_ENTRY := run_tests.py
FAILED_STRING := FAILED

BLENDFILE := test_universal.blend
LOGFILE := unittest.log

PEP8_FLAGS := --ignore=E501 --show-source


all: test

test: clean pep8 binary-exists
	@echo "Running unittests"
	$(BLENDER) $(TEST_DIRECTORY)/$(BLENDFILE) $(TEST_FLAGS) --python $(TEST_ENTRY)

test-ci: clean pep8 binary-exists
	@echo "Running continuous integration unittests"
	$(BLENDER) $(TEST_DIRECTORY)/$(BLENDFILE) $(TEST_FLAGS) --python $(TEST_ENTRY) 2>&1 | tee $(LOGFILE)
	@if grep -q $(FAILED_STRING) $(LOGFILE); then exit 1; fi

binary-exists:
	@if [ -z $(BLENDER) ]; then echo "Blender binary path not set"; exit 1; fi
	@if [ ! -x $(BLENDER) ]; then echo "Blender binary is missing or it is not executable"; exit 1; fi

clean:
	@echo "Removing logfiles"
	rm -rf ./$(LOGFILE)
	@echo "Removing cached python files"
	find . \( -name "__pycache__" -o -name "*.pyc" \) -delete

pep8:
	@echo "Checking pep8 compliance"
	pep8 $(SOURCE_DIRECTORY) $(PEP8_FLAGS)

.PHONY: test test-ci check-binary clean
