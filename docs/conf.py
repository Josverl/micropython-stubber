# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sys
from pathlib import Path

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

src_path = str(Path("..") / "src" / "micropython-stubber")
if src_path not in sys.path:
    sys.path.append(src_path)

# from stubber.version import __version__ as MODULE_VERSION

# Q&D Location
path = Path(__file__).resolve().parents[1] / "pyproject.toml"
pyproject = tomllib.loads(open(str(path)).read())
MODULE_VERSION = pyproject["tool"]["poetry"]["version"]

# -- Project information -----------------------------------------------------

project = "Micropython-Stubber"
copyright = "2019-.... , Jos Verlinde"
author = "Jos Verlinde"

# The full version, including alpha/beta/rc tags
version = release = MODULE_VERSION


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",  # use .md documents
    "sphinxcontrib.mermaid",  # mermaid diagrams
    "autoapi.extension",  # Automatically generate documention from source
    "sphinx.ext.autosummary",  # Generate autodoc summaries
    "sphinx.ext.autodoc",  # Support for NumPy and Google style docstrings
    "sphinx.ext.coverage",  # Collect doc coverage stats
    "sphinx.ext.napoleon",
    # 'sphinx.ext.doctest', # use Test snippets in the documentation
    "sphinx.ext.intersphinx",  # Link to other projects’ documentation
    # 'sphinx.ext.todo', # Support for todo items
    "sphinx_click",  # Document stubber CLI
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to the document source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

html_logo = "img/stubber-XS.jpg"

autodoc_typehints = "both"

intersphinx_mapping = {
    "stubs": ("https://micropython-stubs.readthedocs.io/en/latest/", None),
    "micropython": ("http://docs.micropython.org/en/latest", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "python": ("https://docs.python.org/3/", None),
}

# --- Myst ------

# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#auto-generated-header-anchors
myst_heading_anchors = 2

suppress_warnings = ["myst.header"]
# --- AutoAPI ------
# Generate documentation for the source code in
# https://sphinx-autoapi.readthedocs.io/en/latest/tutorials.html#setting-up-automatic-api-documentation-generation

autoapi_dirs = ["../src/stubber"]
autoapi_root = "api"
autoapi_file_patterns = ["*.py"]
autoapi_keep_files = True  # true for debugging

# only generate documentation for the useful parts
autoapi_ignore = [
    "*migrations*",
    "*/version.py",  # not relevant
    "*/micropip.py",  # not my code
    "*/make_stub_files.py",  # not my code
    "*/stubs/**",  # skip the stubs folder (as it will fail on that)
    "*/boot.py",  # not relevant
    "*/logging.py",  # not relevant
    "*/main.py",  # not relevant
    "*/test*.*",
    "*_partials/*.py",
    "*_min*",  # duplicate code
    "*_lvgl*",  # duplicate code
]

# -- allow for documenting micropython -------------------------------------------------
autodoc_mock_imports = ["micropython", "uos", "uio", "utime", "ujson", "machine", "network"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
try:
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path(), "."]
except ImportError:
    html_theme = "default"
    html_theme_path = ["."]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- set custom width -------------------------------------------------
# ref: https://stackoverflow.com/questions/23211695/modifying-content-width-of-the-sphinx-theme-read-the-docs
def setup(app):
    app.add_css_file("wide_theme.css")
