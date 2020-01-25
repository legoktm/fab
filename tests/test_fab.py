from pathlib import Path
import json

root = Path(__file__).parent.parent
config = json.load((root / "test_config.json").open(encoding="utf-8"))


def test_true():
    assert True
