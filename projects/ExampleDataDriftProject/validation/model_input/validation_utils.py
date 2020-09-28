""" Common functions across validation scripts
"""

import numpy as np
import json
import pandas as pd
import os
import copy


def get_unique_vals(df, feature, group_col, group_value):
    """ Return unique values. Writing as function for testing purposes.

    Inputs:
        df (pd.DataFrame): Pandas DataFrame containing data.
        feature (str): Feature name.
        group_col (str): Name of column to group results by.
        group_value (str): Names of a specific group in group_col.
    """
    return list(df.loc[df[group_col] == group_value][feature].unique())


def initialize_validation_output_dict(modelID, feature, group_col, group_values):
    """ Initialize the dictionary that will be converted to JSON at the end.

    Inputs:
        modelID (int): Model ID number associated with the input feature table.
        feature (str): Name of feature that will be monitored.
        group_col (str): Name of column to group results by.
        group_values (str): Names of specific groups in group_col.

    Returns:
        new_dict (dict): Dictionary containing temporary values that will be replaced.
    """

    # Create the dictionary
    new_dict = {
        "metadata": {"modelID": modelID},
        "schema_validation": {
            group_col: {group_value: {} for group_value in group_values},
        },
    }

    return new_dict


def update_json_dict(dict1, dict2):
    """ Update the results json file with new results.

    Input:
        dict1 (dict): Dictionary loaded in from .json file.
        dict2 (dict): Dictionary created in this script that contains new validation results.

    Returns:
        updated_dict (dict): Updated dictionary that includes results from loaded and new.
    """

    # Using deepcopy to prevent issue where dict1 is overwritten by function call
    loaded_dict = copy.deepcopy(dict1)
    output_dict = copy.deepcopy(dict2)

    # Get IDs
    group_col = list(loaded_dict["schema_validation"].keys())[0]
    group_values = list(loaded_dict["schema_validation"][group_col].keys())

    for group_value in group_values:
        items = list(output_dict["schema_validation"][group_col][group_value].items())[
            0
        ]

        loaded_dict["schema_validation"][group_col][group_value].update(
            {items[0]: items[1]}
        )

    updated_dict = loaded_dict

    return updated_dict


# Create encoder to allow writing numpy format to JSON file
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def write_out_to_json(out_file_name, output_dict):
    """ Write results dictionary to .json file.

    Input:
        out_file_name (str): Name of .json file that will be created from output_dict (e.g., validation_results.json).
        output_dict (dict): Dictionary created in this script that contains new validation results.
    """

    try:
        # Load json file if it exists
        with open(out_file_name) as json_file:
            loaded_dict = json.load(json_file)

        # Update output_dict to contain other feature results
        output_dict = update_json_dict(loaded_dict, output_dict)
        print("Updating {0}".format(out_file_name))
    except FileNotFoundError:
        print("Creating {0}".format(out_file_name))

    # Write to file
    with open(out_file_name, "w") as fp:
        json.dump(output_dict, fp, cls=NpEncoder)

    print("See {0} for structured validation results.".format(out_file_name))


def write_out_to_csv(csv_name, df):
    """ Write results to .csv file that can easily be written to SQL in future.

    Input:
        csv_name (str): Name of csv file to be written (e.g., validation_results.csv).
        df (pd.DataFrame): Pandas DataFrame to be written.
    """

    if os.path.isfile(csv_name):
        # File exists, append
        df.to_csv(csv_name, index=False, mode="a", header=False)
    else:
        # File does not yet exist, create
        df.to_csv(csv_name, index=False, header=True)

    print("See {0} for validation results in csv table format.".format(csv_name))


def construct_schema_drift_row(group_col, group_value, feature, features, modelID=None):
    """ Create a single row of data to be added to the schema drift results table.

    Inputs:
        group_col (str): Name of column to group results by.
        group_value (str): Name of a specific group in group_col.
        feature (str): Name of feature
        features (dict): Dictionary containing information for each feature
        modelID (int): Model ID number associated with the input feature table.

    Returns:
        row (dict): A dictionary representation of the row
    """

    row = {}
    row["modelID"] = modelID
    row["group_col"] = group_col
    row["group_value"] = group_value
    row["feature"] = feature
    row["statusMsg"] = features["status"]
    row["nValues"] = features["n_vals"]

    return row


def create_dataframe(data, group_col, group_values, modelID, metrics_df=None):
    """ Creates the Drift details dataframe
    Input:
        data (dict): Dictionary of data from schema validation
        group_col (str): Name of column to group results by.
        group_value (str): Name of a specific group in group_col.
    Returns:
        metrics_df (pd.DataFrame): dataframe of the input dictionary
    """
    metrics = []

    for group_value in group_values:
        features = data[group_col][group_value]
        for feature in features:
            row_dict = construct_schema_drift_row(
                group_col, group_value, feature, features[feature], modelID,
            )
            metrics.append(row_dict)
    current_df = pd.DataFrame(metrics)

    if metrics_df is None or metrics_df.empty:
        metrics_df = current_df
    else:
        metrics_df = metrics_df.append(current_df)

    return metrics_df
