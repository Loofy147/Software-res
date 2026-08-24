import json
from pathlib import Path
from importlib import resources

from resilience_poc.cli import run_experiment
from resilience_poc.metrics import summarize



def test_experiments_a_to_e_decisions():
    names = ["A", "B", "C", "D1", "D2", "E"]
    results = [run_experiment(name) for name in names]
    expected = {
        "A": "AUTO_MERGE",
        "B": "REJECT",
        "C": "REJECT",
        "D1": "AUTO_MERGE",
        "D2": "REJECT",
        "E": "REJECT",
    }
    for r in results:
        assert r["result"]["status"] == "completed"
        assert r["decision"] == expected[r["experiment"]]

    assert results[1]["result"]["reliability_vector"]["dependency"]["failure_codes"] == ["DEP_DRIFT"]
    assert results[2]["result"]["reliability_vector"]["semantic"]["failure_codes"] == ["SEM_INV_VIOLATION"]
    assert results[4]["result"]["reliability_vector"]["reproducibility"]["failure_codes"] == ["NOT_REPRODUCIBLE"]
    assert results[5]["result"]["reliability_vector"]["concurrency"]["failure_codes"] == ["UNEXPECTED_GIL_REACTIVATION"]


def test_experiment_contracts_are_json():
    fixtures = resources.files('resilience_poc').joinpath('resources','fixtures','experiments')
    for d in fixtures.iterdir():
        if d.is_dir():
            p = d.joinpath('01_generated_patch.json')
            obj = json.loads(p.read_text(encoding='utf-8'))
            assert obj['id']
            assert 'agent_metadata' in obj
