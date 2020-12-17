"""
Sphinx configuration file.

For a full list of available options, see:
https://www.sphinx-doc.org/en/master/usage/configuration.html

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import os
import re
import sys

sys.path.insert(0, os.path.abspath("."))

from custom_directives import (
    CustomButtonDirective,
    CustomCalloutItemDirective,
    CustomCardItemDirective,
)
from redirects import generate_redirects

import fiftyone.constants as foc


with open("../../setup.py") as f:
    setup_version = re.search(r'version="(.+?)"', f.read()).group(1)

if setup_version != foc.VERSION:
    raise RuntimeError(
        "FiftyOne version in setup.py (%r) does not match installed version "
        "(%r). If this is a dev install, reinstall with `pip install -e .` "
        "and try again." % (setup_version, foc.VERSION)
    )


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#


# -- Project information -----------------------------------------------------

project = "FiftyOne"
copyright = foc.COPYRIGHT
author = foc.AUTHOR
release = foc.VERSION


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "nbsphinx",
    "sphinx_tabs.tabs",
    "sphinx_copybutton",
    "autodocsumm",
]

# Types of class members to generate documentation for.
autodoc_default_options = {
    "members": True,
    "inherited-members": True,
    "member-order": "bysource",
    "autosummary": True,
    "autosummary-no-nesting": True,
}
autodoc_inherit_docstrings = True
autoclass_content = "class"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of strings.
source_suffix = [".rst", ".md"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_includes"]

# A string of reStructuredText that will be included at the beginning of every
# source file that is read
rst_prolog = """
.. include:: /_includes/substitutions.rst
"""

# Disable nbshinx loading require.js - this breaks the pytorch theme's
# scrolling handling, and we don't appear to have any notebook content that
# requires it
nbsphinx_requirejs_path = ""

# Adds a link to download the notebook to the built HTML
nbsphinx_prolog = """

.. raw:: html

    <table class="fo-notebook-links" align="left">
        <td>
            <a target="_blank" href="https://colab.research.google.com/github/voxel51/fiftyone/blob/develop/docs/source/{{ env.doc2path(env.docname, base=None) }}">
                <img src="../_static/images/logo/colab-logo-32px.png"/>Run in Google Colab
            </a>
        </td>
        <td>
            <a target="_blank" href="https://github.com/voxel51/fiftyone/blob/develop/docs/source/{{ env.doc2path(env.docname, base=None) }}">
                <img src="../_static/images/logo/github-logo-32px.png"/>View source on GitHub
            </a>
        </td>
        <td>
            <a target="_blank" href="https://raw.githubusercontent.com/voxel51/fiftyone/blob/develop/docs/source/{{ env.doc2path(env.docname, base=None) }}" download>
                <img src="../_static/images/logo/download-logo-32px.png"/>Download notebook
            </a>
        </td>
    </table>

"""

# Path to the redirects file, relative to `source/`
redirects_file = "redirects"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pytorch_sphinx_theme"
html_theme_path = ["../theme"]
html_theme_options = {
    "pytorch_project": "docs",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = ["css/voxel51-website.css", "css/custom.css"]
html_js_files = ["js/voxel51-website.js", "js/custom.js"]

# Prevent RST source files from being included in output
html_copy_source = False

html_context = {
    "address_main_line1": "410 N 4th Ave, 3rd Floor",
    "address_main_line2": "Ann Arbor, MI 48104",
    "phone_main": "+1 734-489-1134",
    "email_info": "info@voxel51.com",
    # Links - copied from website config
    "link_blog": "https://blog.voxel51.com/",
    "link_contactus": "mailto:solutions@voxel51.com?subject=[Voxel51]%20Contact%20us",
    "link_docs_fiftyone": "https://voxel51.com/docs/fiftyone/",
    "link_fiftyone": "https://voxel51.com/fiftyone/",
    "link_fiftyone_tutorials": "https://voxel51.com/docs/fiftyone/tutorials/index.html",
    "link_fiftyone_examples": "https://github.com/voxel51/fiftyone-examples",
    "link_github": "https://github.com/",
    "link_home": "https://voxel51.com/",
    "link_linkedin": "https://www.linkedin.com/in/",
    "link_ourstory": "https://voxel51.com/ourstory/",
    "link_press": "https://voxel51.com/press/",
    "link_privacypolicy": "https://voxel51.com/privacy/",
    "link_schedulecall": "mailto:solutions@voxel51.com?subject=[Voxel51]%20Schedule%20a%20call",
    "link_scheduledemo": "https://meetings.hubspot.com/michael908",
    "link_termsofservice": "https://voxel51.com/terms/",
    "link_twitter": "https://twitter.com/",
    "link_usecase_advertising": "https://voxel51.com/usecases/advertising/",
    "link_usecase_auto": "https://voxel51.com/usecases/automotive/",
    "link_usecase_research": "https://voxel51.com/usecases/research/",
    "link_usecases": "https://voxel51.com/usecases/",
    "link_usecases_entry": "https://voxel51.com/usecases/automotive/",
    "link_voxel51_facebook": "https://www.facebook.com/voxel51/",
    "link_voxel51_github": "https://github.com/voxel51/",
    "link_voxel51_linkedin": "https://www.linkedin.com/company/voxel51/",
    "link_voxel51_slack": "https://join.slack.com/t/fiftyone-users/shared_invite/zt-gtpmm76o-9AjvzNPBOzevBySKzt02gg",
    "link_voxel51_twitter": "https://twitter.com/voxel51",
    "link_voxel51_medium": "https://medium.com/voxel51/",
    # Banner - set to None or empty string to disable
    # "banner_link": "https://us02web.zoom.us/meeting/register/tZ0kd-GppzsrHNeJEEYcCKsE_t_lI_7iB6Sy",
    # "banner_message": "Register for <b>the biweekly FiftyOne webinar series</b> on Wednesdays at 1PM EST!",
    "banner_link": None,
    "banner_message": None,
}

# -- Custom app setup --------------------------------------------------------


def setup(app):
    # Generate page redirects
    app.add_config_value("redirects_file", "redirects", "env")
    app.connect("builder-inited", generate_redirects)

    # Custom directives
    app.add_directive("custombutton", CustomButtonDirective)
    app.add_directive("customcalloutitem", CustomCalloutItemDirective)
    app.add_directive("customcarditem", CustomCardItemDirective)
