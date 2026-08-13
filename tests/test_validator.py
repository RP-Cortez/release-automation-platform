"""Unit tests for the Config Validation Engine."""

from pathlib import Path

import pytest

from src.validator import load_file, validate_config


@pytest.fixture
def schema_path(tmp_path: Path) -> Path:
    """Fixture to generate a temporary JSON schema file."""
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(
        "{\n"
        '  "$schema": "http://json-schema.org/draft-07/schema#",\n'
        '  "type": "object",\n'
        '  "properties": {\n'
        '    "app_name": {"type": "string"}\n'
        "  },\n"
        '  "required": ["app_name"]\n'
        "}"
    )
    return schema_file


def test_load_valid_yaml(tmp_path: Path) -> None:
    """Verify loading and parsing of a valid YAML file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("app_name: test-app\n")
    data = load_file(config_file)
    assert data == {"app_name": "test-app"}


def test_load_file_not_found() -> None:
    """Verify FileNotFoundError is raised when file does not exist."""
    with pytest.raises(FileNotFoundError):
        load_file(Path("non_existent_file.yaml"))


def test_load_unsupported_format(tmp_path: Path) -> None:
    """Verify ValueError is raised for unsupported extensions."""
    invalid_file = tmp_path / "config.txt"
    invalid_file.write_text("app_name = test")
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_file(invalid_file)


def test_validate_config_success(schema_path: Path) -> None:
    """Verify validation succeeds with valid payload."""
    valid_data = {"app_name": "valid-app"}
    assert validate_config(valid_data, schema_path) is True


def test_validate_config_failure(schema_path: Path) -> None:
    """Verify validation fails with invalid data types."""
    invalid_data = {"app_name": 12345}  # Schema expects string, provided int
    assert validate_config(invalid_data, schema_path) is False
