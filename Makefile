.PHONY: test test-ci check-binary clean

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
TESTS_DIRECTORY := $(SOURCE_DIRECTORY)/tests
RUN := run_tests.py
BLENDFILE := test_universal.blend
LOGFILE := unittest.log
FLAGS := -b -noaudio
FAILED_STRING := FAILED

all: test

test: clean lint binary-exists
	@echo "Running unittests"
	@$(BLENDER) $(TESTS_DIRECTORY)/$(BLENDFILE) $(FLAGS) -P $(RUN)

test-ci: clean lint binary-exists
	@echo "Running continuous integration unittests"
	@$(BLENDER) $(TESTS_DIRECTORY)/$(BLENDFILE) $(FLAGS) -P $(RUN) 2>&1 | tee $(LOG)
	@if grep -q $(FAILED_STRING) $(LOG); then exit 1; fi

binary-exists:
	@if [ -z $(BLENDER) ]; then echo "Blender binary path not set"; exit 1; fi
	@if [ ! -x $(BLENDER) ]; then echo "Blender binary is missing or it is not executable"; exit 1; fi

clean:
	@echo "Removing logfiles"
	@rm -rf ./$(LOGFILE)
	@echo "Removing cached python files"
	@find ./ \( -name "__pycache__" -o -name "*.pyc" \) -delete

lint:
	@echo "Checking pep8 compliance"
	@pep8 $(SOURCE_DIRECTORY) --ignore=E501 --show-source
