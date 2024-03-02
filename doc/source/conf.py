# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'EvaICS addon for HomeAssistant'
copyright = '2024, Alexander K'
author = 'Alexander K'

import os, shutil, jinja2

sphinx_root = os.path.dirname(__file__)
sources_root = os.path.normpath(os.path.join(sphinx_root, "../../eva_ics"))

addon_docs = os.path.normpath(os.path.join(sphinx_root, "external"))
os.makedirs(addon_docs, exist_ok=True)
shutil.rmtree(addon_docs)
os.makedirs(addon_docs, exist_ok=True)
indexes = []
shutil.copytree(sources_root+"/hassio", addon_docs+"/hassio", dirs_exist_ok=True)
extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinxcontrib.autodoc_pydantic',
    'sphinx.ext.autosummary',
    "sphinx_immaterial",
    'sphinx.ext.autosectionlabel'
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_immaterial'

import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), 'external/hassio/modbus2mqtt'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'external/hassio/lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'external/hassio/lib/modbus2mqtt'))

