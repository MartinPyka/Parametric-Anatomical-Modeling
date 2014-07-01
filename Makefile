.PHONY: tests

UNAME := $(shell uname -s)
CURRENT_DIR := $(shell pwd)

ifeq ($(UNAME),Darwin)
	BLENDER := /Applications/Blender/blender.app/Contents/MacOS/blender
endif
ifeq ($(UNAME),Linux)
	# TODO(SK): Linux blender executable filepath missing
	BLENDER :=
endif

TEST_DIR := $(CURRENT_DIR)/src/test
TEST_BLENDFILE := test_universal.blend
TEST_FILE := test.py
TEST_FLAGS := -b

default: test

test: 
	$(BLENDER) $(TEST_DIR)/$(TEST_BLENDFILE) $(TEST_FLAGS) -P $(TEST_DIR)/$(TEST_FILE)
