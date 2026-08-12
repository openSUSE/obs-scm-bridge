import json
from pathlib import Path
import yaml
from jsonschema import validate, ValidationError, SchemaError


def validate_yaml_against_schema(yaml_path: str, schema_path: str) -> bool:
    # 1. Load the YAML data file
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            # Use safe_load to avoid executing arbitrary code
            yaml_data = yaml.safe_load(f)
    except yaml.YAMLError as err:
        print(f"❌ Error parsing YAML file: {err}")
        return False

    # 2. Load the JSON Schema file (can be .json or .yaml)
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            if schema_path.endswith((".yaml", ".yml")):
                schema_data = yaml.safe_load(f)
            else:
                schema_data = json.load(f)
    except (json.JSONDecodeError, yaml.YAMLError) as err:
        print(f"❌ Error parsing Schema file: {err}")
        return False

    # 3. Validate YAML data against Schema
    try:
        validate(instance=yaml_data, schema=schema_data)
        print("✅ Validation successful! YAML file matches the schema.")
        return True

    except ValidationError as err:
        print("❌ Validation Failed!")
        print(f"  • Message: {err.message}")
        print(f"  • Failed Path in YAML: {' -> '.join(str(p) for p in err.absolute_path)}")
        return False

    except SchemaError as err:
        print(f"❌ The JSON schema itself is invalid: {err.message}")
        return False


def test_validate():
    validate_yaml_against_schema("example/_manifest", "manifest_schema.json")
