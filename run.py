#!/usr/bin/env python3
"""Convenience launcher for MINDSPACE — Your Personal Space."""

import sys
from pathlib import Path

# Ensure mindspace package directory is on sys.path
root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from mindspace.main import main

if __name__ == "__main__":
    main()

