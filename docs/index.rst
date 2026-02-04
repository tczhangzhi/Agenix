.. Agenix documentation master file

Welcome to Agenix's documentation!
===================================

Agenix is a Python-based AI coding agent that helps you with software development tasks through natural language interactions.

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   cli
   sessions
   settings
   skills
   extensions

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide:

   sdk
   api/modules

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install -e .

Basic Usage
~~~~~~~~~~~

.. code-block:: bash

   # Start a conversation
   agenix "Help me fix this bug"

   # Continue a previous session
   agenix --session my-session "Add unit tests"

Features
--------

* **Natural Language Interface**: Interact with your codebase using plain English
* **Multiple Tools**: Read, write, edit files, run bash commands, and more
* **Session Management**: Continue conversations across multiple interactions
* **Extensible**: Add custom tools and skills to extend functionality
* **LLM Agnostic**: Works with any Anthropic Claude model

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
