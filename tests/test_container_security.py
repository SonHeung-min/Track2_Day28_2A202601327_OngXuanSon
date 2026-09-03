from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_api_image_declares_a_fixed_non_root_user() -> None:
    dockerfile = (ROOT / "docker" / "api" / "Dockerfile").read_text(encoding="utf-8")

    assert "USER 10001:10001" in dockerfile
    assert "useradd --uid 10001 --gid 10001" in dockerfile
