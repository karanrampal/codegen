"""Add unit tests for configuration manager"""

from pathlib import Path

import pytest
import yaml

from config_manager.manager import Params


@pytest.fixture(name="my_tmp_file")
def test_yaml_file(tmpdir: Path) -> str:
    """Fixture to create a temporary yaml file."""
    yaml_content = {"param1": 1, "param2": "value2"}
    yaml_path = Path(tmpdir) / "test.yaml"
    with open(yaml_path, "w", encoding="utf-8") as fptr:
        yaml.safe_dump(yaml_content, fptr)
    return str(yaml_path)


def test_params_init_dict() -> None:
    """Test initializing Params with a dictionary."""
    params = Params({"a": 1, "b": "test"})
    assert params.a == 1
    assert params.b == "test"


def test_params_init_yaml(my_tmp_file: str) -> None:
    """Test initializing Params with a yaml file."""
    params = Params(my_tmp_file)
    assert params.param1 == 1
    assert params.param2 == "value2"


def test_params_update_dict() -> None:
    """Test updating Params with a dictionary."""
    params = Params({"a": 1})
    params.update({"b": 2, "c": "test"})
    assert params.a == 1
    assert params.b == 2
    assert params.c == "test"


def test_params_update_yaml(my_tmp_file: str) -> None:
    """Test updating Params with a yaml file."""
    params = Params({"a": 1})
    params.update(my_tmp_file)
    assert params.a == 1
    assert params.param1 == 1
    assert params.param2 == "value2"


def test_params_save(tmpdir: Path, my_tmp_file: str) -> None:
    """Test saving Params to a yaml file."""
    params = Params(my_tmp_file)
    save_path = Path(tmpdir) / "saved_params.yaml"
    params.save(str(save_path))
    with open(save_path, "r", encoding="utf-8") as fptr:
        saved_params = yaml.safe_load(fptr)
    assert saved_params == {"param1": 1, "param2": "value2"}


def test_params_str() -> None:
    """Test string representation of Params."""
    params = Params({"a": 1, "b": "test"})
    assert str(params) == "{'a': 1, 'b': 'test'}"


def test_params_invalid_input() -> None:
    """Test raising TypeError for invalid input."""
    with pytest.raises(TypeError):
        Params(123)  # type: ignore[arg-type]
