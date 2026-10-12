#!/usr/bin/env python3
"""Compatibility wrapper for the canonical Streamlit UI.

Run this file directly via streamlit, or launch the canonical app from the
project root with:
    python run_pipeline.py --ui
"""

from src.hitl_writeback_ui import main

if __name__ == "__main__":
    main()
