#!/usr/bin/env python3
from pathlib import Path

from src.config import ARTIFACTS_DIR
from src.generate_charts import generate_charts
from src.generate_pdf_report import build_pdf
from src.generate_powerpoint_report import create_deck

ROOT = Path(__file__).resolve().parents[1]


def test_report_artifacts_are_generated() -> None:
    generate_charts()
    build_pdf()
    create_deck()

    report_dir = ARTIFACTS_DIR / "reports"
    expected_files = [
        report_dir / "chart_bomiljo_monthly.png",
        report_dir / "chart_komskole_units.png",
        report_dir / "chart_netzero_waterfall.png",
        report_dir / "Kristiansand_EPM_Status_Prognose_Tiltaksrapport.pdf",
        report_dir / "Kristiansand_EPM_Status_Prognose_Tiltaksrapport.pptx",
    ]

    for file_path in expected_files:
        assert file_path.exists(), f"Expected generated artifact at {file_path}"
        assert file_path.stat().st_size > 0, f"Artifact should not be empty: {file_path}"

    assert report_dir.is_dir()
    assert report_dir.parent == ARTIFACTS_DIR
    assert ROOT / "reports" != report_dir
