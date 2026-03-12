from io import StringIO

import pytest

from esoreader import EsoFile


@pytest.fixture
def eso():
    content = StringIO(
        "Version,Timestamp,1.0,2025-09-26\n"
        "1,4,Zone1,Zone Ventilation Total Heat Loss Energy [J] !TimeStep\n"
        "End of Data Dictionary\n"
        "1,100.0\n"
        "1,200.0\n"
        "End of Data\n"
    )
    return EsoFile(content)


def test_data_dictionary_parsing(eso):
    assert len(eso.dd.variables) == 1

    timestep, key, name, unit = eso.dd.variables[1]
    assert (timestep, key, name) in eso.dd.index


def test_data_parsing(eso):
    assert eso.data[1] == [100.0, 200.0]


@pytest.mark.parametrize(
    "query, expected_zone",
    [
        pytest.param("heat loss", "Zone1", id="match_by_substring"),
    ],
)
def test_find_variable(eso, query, expected_zone):
    result = eso.find_variable(query)
    assert len(result) == 1
    assert result[0][1] == expected_zone
