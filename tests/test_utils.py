import pytest
import json
from buda.utils import load_data

def test_load_data(mocker):
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data='{"key": "value"}'))
    result = load_data("dummy_path")
    mock_open.assert_called_once_with("dummy_path", "r")
    assert result == {"key": "value"}

def test_load_data_invalid_json(mocker):
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data='invalid json'))
    with pytest.raises(json.JSONDecodeError):
        load_data("dummy_path")
        def test_load_data(mocker):
            mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data='{"key": "value"}'))
            result = load_data("dummy_path")
            mock_open.assert_called_once_with("dummy_path", "r")
            assert result == {"key": "value"}

        def test_load_data_invalid_json(mocker):
            mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data='invalid json'))
            with pytest.raises(json.JSONDecodeError):
                load_data("dummy_path")

        def test_load_data_file_not_found(mocker):
            mocker.patch("builtins.open", side_effect=FileNotFoundError)
            with pytest.raises(FileNotFoundError):
                load_data("dummy_path")

        def test_load_data_empty_file(mocker):
            mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data=''))
            with pytest.raises(json.JSONDecodeError):
                load_data("dummy_path")
