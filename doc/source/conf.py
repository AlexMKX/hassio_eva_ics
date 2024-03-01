# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'eva_ics'
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
for directory, subdirectories, files in os.walk(sources_root):
    if os.path.basename(directory) == "doc":
        target = os.path.join(addon_docs, directory[len(sources_root) + 1:])
        os.makedirs(target, exist_ok=True)
        shutil.copytree(directory, target, dirs_exist_ok=True)
        indexes.append(os.path.join('external', directory[len(sources_root) + 1:], 'index.rst'))

env = jinja2.Environment(loader=jinja2.FileSystemLoader(sphinx_root))
template = env.get_template('indices.rst.j2')
with open(os.path.join(sphinx_root, 'indices.rst'), 'w') as f:
    f.write(template.render(indices=indexes))
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinxcontrib.autodoc_pydantic',
    'sphinx.ext.autosummary',
    'sphinx_markdown_builder',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../eva_ics/hassio/lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../eva_ics/hassio/modbus2mqtt'))
autosummary_generate = True
