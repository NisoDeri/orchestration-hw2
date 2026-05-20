"""Shared infrastructure — config, logger (FIFO), gatekeeper, version.

These modules underpin every other layer; they depend on nothing project-local
except ``models/`` for typed config schemas.
"""
