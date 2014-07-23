import os
import site
import sys

try:
    import sphinx
except ImportError:
    print("Sphinx not installed")
    sys.exit(1)

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
BUILD_DIR = os.path.join(CURRENT_DIR, "_build")

sys.path.insert(0, os.path.join(CURRENT_DIR, ".."))

if __name__ == "__main__":
    argv = ["sphinx-build", "-b", "html", CURRENT_DIR, BUILD_DIR]
    sphinx.main(argv)
