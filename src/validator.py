#!/usr/bin/env python3
"""Config Validation CLI Engine for Release Automation Platform."""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, cast

import jsonschema
import yaml

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("config-validator")


def load_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a YAML or JSON file."""
    if not file_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        if file_path.suffix in [".yaml", ".yml"]:
            data = yaml.safe_load(file)  # Assign to variable, do not return yet
        elif file_path.suffix == ".json":
            data = json.load(file)  # Assign to variable, do not return yet
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid file content in {file_path}: expected mapping/dictionary"
        )

    return cast(Dict[str, Any], data)


def validate_config(config_data: Dict[str, Any], schema_path: Path) -> bool:
    """Validate configuration dict against a JSON schema."""
    schema = load_file(schema_path)

    try:
        jsonschema.validate(instance=config_data, schema=schema)
        logger.info("Configuration validation succeeded.")
        return True
    except jsonschema.ValidationError as err:
        logger.error(f"Validation failed: {err.message}")
        return False
    except jsonschema.SchemaError as err:
        logger.critical(f"Invalid JSON Schema definition: {err.message}")
        return False


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Validate application deployment configurations."
    )
    parser.add_argument(
        "--config",
        "-c",
        required=True,
        type=Path,
        help="Path to the configuration file (YAML/JSON)",
    )
    parser.add_argument(
        "--schema",
        "-s",
        required=True,
        type=Path,
        help="Path to the JSON schema validation file",
    )

    args = parser.parse_args()

    try:
        config_data = load_file(args.config)
        is_valid = validate_config(config_data, args.schema)

        if is_valid:
            sys.exit(0)
        else:
            sys.exit(1)

    except (FileNotFoundError, ValueError, yaml.YAMLError, json.JSONDecodeError) as e:
        logger.error(f"Execution failed: {str(e)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
