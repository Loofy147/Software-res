from importlib import resources
import json


def test_packaged_schemas_and_fixtures_are_available():
    pkg = resources.files("resilience_poc")
    schemas = pkg.joinpath("resources", "schemas")
    fixtures = pkg.joinpath("resources", "fixtures", "experiments")

    schema_files = sorted(p.name for p in schemas.iterdir() if p.name.endswith(".json"))
    fixture_dirs = sorted(p.name for p in fixtures.iterdir() if p.is_dir())

    assert len(schema_files) == 5
    assert fixture_dirs == ["A", "B", "C", "D1", "D2", "E"]
    for name in schema_files:
        json.loads(schemas.joinpath(name).read_text(encoding="utf-8"))
