.PHONY: test test-ci check-binary

UNAME := $(shell uname -s)
PWD := $(shell pwd)

ifdef CI
	BLENDER := $(BLENDER_BIN)
else ifeq ($(UNAME),Linux)
	# TODO(SK): Linux blender executable filepath missing
	BLENDER :=
else ifeq ($(UNAME),Darwin)
	BLENDER := /Applications/Blender/blender.app/Contents/MacOS/blender
endif

TEST_DIR := $(PWD)/pam/tests
TEST_BLENDFILE := test_universal.blend
TEST_FILE := run_tests.py
TEST_LOG := unittest.log
TEST_FLAGS := -b -noaudio
TEST_FAILED := FAILED

test: binary-exists
	@echo "Running tests"
	@$(BLENDER) $(TEST_DIR)/$(TEST_BLENDFILE) $(TEST_FLAGS) -P $(TEST_FILE)

test-ci: binary-exists
	@echo "Running continuous integration tests"
	@$(BLENDER) $(TEST_DIR)/$(TEST_BLENDFILE) $(TEST_FLAGS) -P $(TEST_FILE) 2>&1 | tee $(TEST_LOG)
	@if grep -q $(TEST_FAILED) $(TEST_LOG); then exit 1; fi

binary-exists:
	@if [ -z $(BLENDER) ]; then echo "Blender binary path not set"; exit 1; fi
	@if [ ! -x $(BLENDER) ]; then echo "Blender binary is missing or not executable"; exit 1; fi
