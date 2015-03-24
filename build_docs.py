import os
import site
import sys

try:
    import sphinx
except ImportError:
    print("Sphinx not installed")
    sys.exit(1)

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
DOCS_DIR = os.path.join(CURRENT_DIR, "docs")
BUILD_DIR = os.path.join(DOCS_DIR, "_build")

sys.path.insert(0, CURRENT_DIR)

if __name__ == "__main__":
    argv = ["sphinx-build", "-b", "html", DOCS_DIR, BUILD_DIR]
    sphinx.main(argv)
