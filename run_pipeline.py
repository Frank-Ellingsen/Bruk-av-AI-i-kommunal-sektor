#!/usr/bin/env python3
"""Small project launcher for the Kristiansand EPM workflow.

Usage examples:
  python run_pipeline.py --etl
  python run_pipeline.py --ui
  python run_pipeline.py --all
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_script(script_path: str) -> None:
    subprocess.run([sys.executable, str(ROOT / script_path)], cwd=str(ROOT), check=True)


def run_streamlit_app() -> None:
    streamlit_executable = shutil.which("streamlit")
    if not streamlit_executable:
        raise RuntimeError("streamlit is not installed or not on PATH. Install dependencies via: pip install -r requirements.txt")
    subprocess.run([streamlit_executable, "run", str(ROOT / "hitl_writeback_ui.py")], cwd=str(ROOT), check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Kristiansand EPM ETL and/or HITL UI.")
    parser.add_argument("--etl", action="store_true", help="Build the Golden Record database from source CSV files.")
    parser.add_argument("--ui", action="store_true", help="Launch the Streamlit HITL governance portal.")
    parser.add_argument("--all", action="store_true", help="Run ETL and launch the UI.")
    args = parser.parse_args()

    run_all = args.all or not (args.etl or args.ui)

    if args.etl or run_all:
        print("[INFO] Building the Golden Record database...")
        run_script("src/build_golden_record.py")

    if args.ui or run_all:
        print("[INFO] Launching the HITL governance portal...")
        run_streamlit_app()


if __name__ == "__main__":
    main()
