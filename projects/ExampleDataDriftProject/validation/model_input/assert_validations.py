""" Cause pipeline to fail if there is at least one schema validation failure
"""

import argparse
import json
import sys
import os

sys.path.append(os.getcwd())
from common.common_utils import format_arg_features  # noqa: E402

# ----------------------
# Functions
# ----------------------


def search_dict_for_invalid(group_col, group_values, features, results, invalids):
    """ Search dictionary for features with invalid schema

    Inputs:
        group_col (str): Name of column to group results by.
        group_values (str): Names of specific groups in group_col.
        features (list of str): List of features that will be monitored.
        results (dict): Dictionary containing schema validation results and metadata.
        invalids (list): List of strings containing information about which features are invalid.

    Return:
        invalids (list): List of strings containing information about which features are invalid.
    """
    for group_value in group_values:
        for feature in features:
            status = results["schema_validation"][group_col][group_value][feature][
                "status"
            ]
            if status.lower() != "valid":
                invalids.append(
                    "{0}: {1}, {2} invalid".format(group_col, group_value, feature)
                )

    return invalids


# ----------------------
# Main
# ----------------------

if __name__ == "__main__":
    # Read in arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--modelID", type=int, required=True, help="Model ID number",
    )
    parser.add_argument(
        "-f",
        "--features",
        type=str,
        required=True,
        help="Comma separated list of features to monitor (e.g., featureName1,featureName2)",
    )
    parser.add_argument(
        "-g",
        "--group_col",
        type=str,
        required=False,
        default="",
        help="Name of column in data to group by.",
    )
    args = parser.parse_args()

    # Assign arguments to variables
    modelID = args.modelID
    features = format_arg_features(args.features)
    group_col = args.group_col

    # ------------------------------------
    # 1. Read results JSON file
    # ------------------------------------
    results_dict_path = "model-{0}_schema_validation_results.json".format(modelID)
    with open(results_dict_path) as f:
        results = json.load(f)

    if group_col == "":
        group_values = [""]
    else:
        group_values = list(results["schema_validation"][group_col].keys())

    # ------------------------------------------------------------
    # 2. Search for features determined to have invalid schema
    # ------------------------------------------------------------
    # Initialize
    invalids = list()

    # Find invalid features
    invalids = search_dict_for_invalid(
        group_col=group_col,
        group_values=group_values,
        features=features,
        results=results,
        invalids=invalids,
    )

    # ------------------------------------------------------------
    # 3. Break pipeline if any feature input schema are invalid
    # ------------------------------------------------------------
    try:
        assert len(invalids) == 0
        print(
            "Input schema validation for all specified features successful. No invalid input detected."
        )
    except AssertionError:
        print("Input schema invalid for the following features in respective groups...")
        print(invalids)
        assert len(invalids) == 0
