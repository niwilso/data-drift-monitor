""" Test ../validation/model_input/assert_validations.py
"""

import sys
import os

sys.path.append(os.getcwd())
from validation.model_input.assert_validations import (  # noqa: E402
    search_dict_for_invalid,
)


def test_search_dict_for_invalid():
    # Arrange
    test_dict = {
        "metadata": {"modelID": 1},
        "schema_validation": {
            "healthSystemID": {
                "exampleHealthSystemID_1": {
                    "gcsTotalLast": {"status": "valid", "n_vals": 13},
                    "dxGroup": {"status": "valid", "n_vals": 20},
                },
                "exampleHealthSystemID_2": {
                    "gcsTotalLast": {
                        "status": "invalid: range value not in GCS scale range (3-15)",
                        "n_vals": 13,
                    },
                    "dxGroup": {
                        "status": "invalid: at least one value not in list of acceptable values",
                        "n_vals": 20,
                    },
                },
            },
            "hospitalID": {
                "exampleHospitalID_1": {
                    "gcsTotalLast": {"status": "valid", "n_vals": 13},
                    "dxGroup": {"status": "valid", "n_vals": 20},
                },
                "exampleHospitalID_2": {
                    "gcsTotalLast": {
                        "status": "invalid: values in range are not integers",
                        "n_vals": 13,
                    },
                    "dxGroup": {
                        "status": "invalid: at least one value not a string",
                        "n_vals": 20,
                    },
                },
            },
        },
    }

    entityType = "healthSystemID"
    entityIDs = list(test_dict["schema_validation"][entityType].keys())
    features = list(test_dict["schema_validation"][entityType][entityIDs[0]].keys())
    results = test_dict
    invalids = list()

    # Act
    invalids = search_dict_for_invalid(
        entityType, entityIDs, features, results, invalids
    )

    # Assert
    assert type(invalids) == list
    assert len(invalids) == 2
    assert (entityType in invalids[0]) is True
