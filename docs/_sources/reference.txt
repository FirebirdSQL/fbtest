
==================
`fbtest` Reference
==================

.. module:: fbtest
  :synopsis: Core module for running tests against Firebird engine

Globals
=======

.. autodata:: DB_NEW
.. autodata:: DB_EXISTING
.. autodata:: DB_RESTORE
.. autodata:: DB_ACCESS
.. autodata:: CHARACTER_SETS
.. autodata:: PAGE_SIZES
.. autodata:: TYPE_ISQL
.. autodata:: TYPE_PYTHON
.. autodata:: TEST_TYPES
.. autodata:: PLATFORMS
.. autodata:: UNKNOWN
.. data:: script_runner

   :class:`ScriptRunner` instance.

Functions
=========

.. autofunction:: xml_safe
.. autofunction:: escape_cdata
.. autofunction:: trim_value
.. autofunction:: quote
.. autofunction:: compare_versions
.. autofunction:: as_unicode
.. autofunction:: as_utf8
.. autofunction:: runProgram

Classes
=======

TestVersion class
-----------------
.. autoclass:: TestVersion
   :member-order: groupwise
   :members:
   :undoc-members:

Test class
----------
.. autoclass:: Test
   :member-order: groupwise
   :members:
   :undoc-members:

Resource class
--------------
.. autoclass:: Resource
   :member-order: groupwise
   :members:
   :undoc-members:

UserResource class
------------------
.. autoclass:: UserResource
   :member-order: groupwise
   :members:
   :undoc-members:

Suite class
-----------
.. autoclass:: Suite
   :member-order: groupwise
   :members:
   :undoc-members:

Repository class
----------------
.. autoclass:: Repository
   :member-order: groupwise
   :members:
   :undoc-members:

Archive class
-------------
.. autoclass:: Archive
   :member-order: groupwise
   :members:
   :undoc-members:

Result class
------------
.. autoclass:: Result
   :member-order: groupwise
   :members:
   :undoc-members:

RunResults class
----------------
.. autoclass:: RunResults
   :member-order: groupwise
   :members:
   :undoc-members:

Runner class
------------
.. autoclass:: Runner
   :member-order: groupwise
   :members:
   :undoc-members:

ScriptRunner class
------------------
.. autoclass:: ScriptRunner
   :member-order: groupwise
   :members:
   :undoc-members:

Script Functions
================

.. autofunction:: run_tests
.. autofunction:: run_server
.. autofunction:: run_analyze
.. autofunction:: run_update
.. autofunction:: run_view
.. autofunction:: run_archive

