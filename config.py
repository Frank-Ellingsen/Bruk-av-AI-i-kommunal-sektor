#!/usr/bin/env python3
"""Compatibility shim for package and script execution.

The project historically imported configuration constants as `from config import ...`
when files were run directly from the src directory. The canonical implementation now
lives under `src/config.py`, and this wrapper keeps older direct-import usage working
when the repository root is on `sys.path`.
"""

from src.config import *
