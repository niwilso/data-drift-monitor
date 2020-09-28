""" Test ../validation/model_input/validation_utils.py
"""

import sys
import os
import pytest
import pandas as pd

sys.path.append(os.getcwd())
from validation.model_input.validation_utils import (  # noqa: E402
    get_unique_vals,
    initialize_validation_output_dict,
    update_json_dict,
    construct_schema_drift_row,
    create_dataframe,
)


# -------------------------------------------------
# Create sample data
# -------------------------------------------------


@pytest.fixture
def dict_gcsTotalLast(scope="function"):
    dict1 = {
        "metadata": {"modelID": 1},
        "schema_validation": {
            "healthSystemID": {
                "exampleHealthSystemID_1": {
                    "gcsTotalLast": {"status": "valid", "n_vals": 13}
                },
                "exampleHealthSystemID_2": {
                    "gcsTotalLast": {
                        "status": "invalid: range value not in GCS scale range (3-15)",
                        "n_vals": 13,
                    }
                },
            },
            "hospitalID": {
                "exampleHospitalID_1": {
                    "gcsTotalLast": {"status": "valid", "n_vals": 13}
                },
                "exampleHospitalID_2": {
                    "gcsTotalLast": {
                        "status": "invalid: values in range are not integers",
                        "n_vals": 13,
                    }
                },
            },
        },
    }

    return dict1


@pytest.fixture
def dict_dxGroup(scope="function"):
    dict2 = {
        "metadata": {"modelID": 1},
        "schema_validation": {
            "healthSystemID": {
                "exampleHealthSystemID_1": {
                    "dxGroup": {"status": "valid", "n_vals": 20}
                },
                "exampleHealthSystemID_2": {
                    "dxGroup": {
                        "status": "invalid: at least one value not in list of acceptable values",
                        "n_vals": 20,
                    }
                },
            },
            "hospitalID": {
                "exampleHospitalID_1": {"dxGroup": {"status": "valid", "n_vals": 20}},
                "exampleHospitalID_2": {
                    "dxGroup": {
                        "status": "invalid: at least one value not a string",
                        "n_vals": 20,
                    }
                },
            },
        },
    }

    return dict2


# -------------------------------------------------
# Unit tests
# -------------------------------------------------


def test_get_unique_vals():
    # Arrange
    feature = "feature01"
    group_col = "hospitalID"
    group_value = "exampleHospitalID1"
    df_temp = pd.DataFrame()
    df_temp[feature] = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
    df_temp[group_col] = [group_value] * len(df_temp[feature])

    # Act
    unique_vals = get_unique_vals(df_temp, feature, group_col, group_value)

    # Assert
    assert len(unique_vals) == 4


def test_initialize_validation_output_dict():
    # Arrange
    modelID = 1
    feature = "gcsTotalLast"
    group_col = "hospitalID"
    group_values = ["exampleHospitalID1", "exampleHospitalID2", "exampleHospitalID3"]

    # Act
    test_dict = initialize_validation_output_dict(
        modelID, feature, group_col, group_values
    )

    # Assert
    assert type(test_dict) == dict


def test_initialize_validation_output_dict_no_group():
    # Arrange
    modelID = 1
    feature = "gcsTotalLast"
    group_col = ""
    group_values = [""]

    # Act
    test_dict = initialize_validation_output_dict(
        modelID, feature, group_col, group_values
    )

    # Assert
    assert type(test_dict) == dict


def test_update_json_dict(dict_gcsTotalLast, dict_dxGroup):
    # Act
    updated_dict = update_json_dict(dict_gcsTotalLast, dict_dxGroup)

    # Assert
    assert type(updated_dict) == dict
    assert len(updated_dict) == len(dict_gcsTotalLast)
    assert updated_dict != dict_gcsTotalLast
    assert updated_dict != dict_dxGroup


@pytest.mark.skip(reason="Requires json file IO")
def test_write_out_to_json():
    print("Skip test_write_out_to_json")


@pytest.mark.skip(reason="Requires csv file IO")
def test_write_out_to_json():
    print("Skip test_write_out_to_csv")


def test_construct_schema_drift_row(dict_gcsTotalLast):
    # Arrange
    entityType = list(dict_gcsTotalLast["schema_validation"].keys())[0]
    entityID = list(dict_gcsTotalLast["schema_validation"][entityType].keys())[0]
    feature = list(dict_gcsTotalLast["schema_validation"][entityType][entityID].keys())[
        0
    ]
    features = dict_gcsTotalLast["schema_validation"][entityType][entityID][feature]
    modelID = dict_gcsTotalLast["metadata"]["modelID"]

    # Act
    row = construct_schema_drift_row(entityType, entityID, feature, features, modelID)

    # Assert
    assert type(row) == dict
    assert len(dict_gcsTotalLast) > 0


def test_create_dataframe_new(dict_gcsTotalLast):
    # Arrange
    data = dict_gcsTotalLast["schema_validation"]
    entityType = list(data.keys())[0]
    entityIDs = list(data[entityType].keys())
    modelID = dict_gcsTotalLast["metadata"]["modelID"]

    # Act
    metrics_df = create_dataframe(data, entityType, entityIDs, modelID)

    # Assert
    assert type(metrics_df) == pd.DataFrame


def test_create_dataframe_append(dict_gcsTotalLast, dict_dxGroup):
    # Arrange
    data = dict_gcsTotalLast["schema_validation"]
    data2 = pd.DataFrame()
    entityType = list(data.keys())[0]
    entityIDs = list(data[entityType].keys())
    modelID = dict_gcsTotalLast["metadata"]["modelID"]

    # Act
    metrics_df = create_dataframe(data, entityType, entityIDs, modelID, data2)

    # Assert
    assert type(metrics_df) == pd.DataFrame
