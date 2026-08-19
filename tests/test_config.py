"""Tests for project configuration."""

from pathlib import Path

from electricvehicles.config import PROJECT_ROOT, get_data_path


def test_default_data_path_is_inside_project(monkeypatch) -> None:
    monkeypatch.delenv("EV_DATA_PATH", raising=False)
    assert get_data_path() == PROJECT_ROOT / "data" / "raw" / "electric.csv"


def test_relative_environment_path_uses_project_root(monkeypatch) -> None:
    monkeypatch.setenv("EV_DATA_PATH", "example/source.csv")
    assert get_data_path() == (PROJECT_ROOT / "example" / "source.csv").resolve()


def test_explicit_path_takes_precedence(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("EV_DATA_PATH", "ignored.csv")
    expected = tmp_path / "source.csv"
    assert get_data_path(expected) == expected.resolve()
