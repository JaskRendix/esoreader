import pandas as pd
import pytest

from esoreader import read_from_path


@pytest.fixture
def eso():
    return read_from_path("tests/mock_eplusout.eso")


def test_data_dictionary_parsing(eso):
    assert len(eso.dd.variables) == 1
    assert eso.dd.variables[1][2] == "Zone Ventilation Total Heat Loss Energy"
    assert eso.dd.variables[1][0] == "TimeStep"


def test_data_values(eso):
    assert eso.data[1] == [100.0, 200.0]


@pytest.mark.parametrize(
    "query, expected_zone",
    [
        pytest.param("heat loss", "Zone1", id="lowercase"),
        pytest.param("HEAT LOSS", "Zone1", id="uppercase"),
    ],
)
def test_find_variable(eso, query, expected_zone):
    result = eso.find_variable(query)
    assert len(result) == 1
    assert result[0][1] == expected_zone


def test_to_frame_output(eso):
    df = eso.to_frame("heat loss")
    assert df.shape == (2, 1)
    assert df.columns[0] == "Zone1"
    assert df.iloc[0, 0] == 100.0
    assert df.iloc[1, 0] == 200.0


def test_variable_unit_parsing(eso):
    assert eso.dd.variables[1][3] == "J"


@pytest.mark.parametrize(
    "key, frequency",
    [
        pytest.param("ZoneX", None, id="wrong_key"),
        pytest.param(None, "Hourly", id="wrong_frequency"),
    ],
)
def test_find_variable_no_results(eso, key, frequency):
    result = eso.find_variable("heat loss", key=key, frequency=frequency)
    assert result == []


def test_to_frame_use_variable_name(eso):
    df = eso.to_frame("heat loss", use_key_for_columns=False)
    assert "Zone Ventilation Total Heat Loss Energy" in df.columns[0]


def test_to_frame_with_custom_index(eso):
    df = eso.to_frame("heat loss", index=["t1", "t2"])
    assert list(df.index) == ["t1", "t2"]


def test_data_dictionary_build_index(eso):
    key = ("TimeStep", "Zone1", "Zone Ventilation Total Heat Loss Energy")
    assert eso.dd.index[key] == 1


def test_reading_version_and_timestamp(eso):
    assert eso.dd.version == "1.0"
    assert eso.dd.timestamp == "2025-09-26"


@pytest.mark.parametrize(
    "query, expected_len",
    [
        pytest.param("Ventilation", 1, id="partial_match"),
        pytest.param("Nonexistent Variable", 0, id="no_match"),
    ],
)
def test_data_dictionary_find_variable(eso, query, expected_len):
    matches = eso.dd.find_variable(query)
    assert len(matches) == expected_len


def test_to_series_output(eso):
    series = eso.to_series("heat loss")
    assert isinstance(series, pd.Series)
    assert series.tolist() == [100.0, 200.0]


def test_to_series_with_key(eso):
    series = eso.to_series("heat loss", key="Zone1")
    assert series.tolist() == [100.0, 200.0]


@pytest.mark.parametrize(
    "query",
    [
        pytest.param("HEAT LOSS", id="uppercase"),
        pytest.param("heat loss", id="lowercase"),
    ],
)
def test_to_series_case_insensitive(eso, query):
    series = eso.to_series(query)
    assert series.iloc[0] == 100.0


@pytest.mark.parametrize(
    "key, frequency",
    [
        pytest.param("ZoneX", None, id="wrong_key"),
        pytest.param(None, "Hourly", id="wrong_frequency"),
    ],
)
def test_to_series_errors(eso, key, frequency):
    with pytest.raises(ValueError, match="No variable found for search: heat loss"):
        eso.to_series("heat loss", key=key, frequency=frequency)
