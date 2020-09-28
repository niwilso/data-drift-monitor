""" Test ../validation/model_input/validate_deaths.py
"""

import sys
import os
import pytest
import pandas as pd

sys.path.append(os.getcwd())
sys.path.append(os.getcwd() + "/validation/model_input")
from validation.model_input.validate_deaths import validate_schema_deaths  # noqa: E402


@pytest.fixture
def validation_dict(scope="module"):
    modelID = 1
    group_col = "healthSystemID"
    group_values = ["exampleHealthSystemID1", "exampleHealthSystemID2"]

    new_dict = {
        "metadata": {"modelID": modelID},
        "schema_validation": {
            group_col: {group_value: {} for group_value in group_values},
        },
    }

    return new_dict


# Test with valid values
@pytest.mark.parametrize(
    "feature_values", [[12345, 1, 0, 9999], [100, 255, 343, 7, 2934],],
)
def test_validate_schema_deaths_valid(monkeypatch, validation_dict, feature_values):
    # Arrange
    group_col = "healthSystemID"
    group_values = ["exampleHealthSystemID1", "exampleHealthSystemID2"]
    feature = "deaths"
    df = pd.DataFrame()

    def mock_get_unique_vals(df, feature, group_col, group_values):
        return feature_values

    # Act
    monkeypatch.setattr(
        "validation.model_input.validate_deaths.get_unique_vals", mock_get_unique_vals,
    )
    output_dict = validate_schema_deaths(
        group_col, group_values, df, feature, validation_dict
    )

    # Assert
    assert type(output_dict) == dict
    assert (
        "invalid"
        in output_dict["schema_validation"][group_col][group_values[0]][feature][
            "status"
        ]
    ) is False


# Test with invalid values
@pytest.mark.parametrize(
    "feature_values", [[0.5, 1, 2, 100], [1, 2, 3, -10]],
)
def test_validate_schema_deaths_invalid(monkeypatch, validation_dict, feature_values):
    # Arrange
    group_col = "healthSystemID"
    group_values = ["exampleHealthSystemID1", "exampleHealthSystemID2"]
    feature = "deaths"
    df = pd.DataFrame()

    def mock_get_unique_vals(df, feature, group_col, group_values):
        return feature_values

    # Act
    monkeypatch.setattr(
        "validation.model_input.validate_deaths.get_unique_vals", mock_get_unique_vals,
    )
    output_dict = validate_schema_deaths(
        group_col, group_values, df, feature, validation_dict
    )

    # Assert
    assert type(output_dict) == dict
    assert (
        "invalid"
        in output_dict["schema_validation"][group_col][group_values[0]][feature][
            "status"
        ]
    )
