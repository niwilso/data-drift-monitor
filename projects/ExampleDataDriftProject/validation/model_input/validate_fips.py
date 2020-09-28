""" Validate values for the feature "fips" have correct schema
"""

import argparse
import mlflow
import os
import sys
import pandas as pd
import numpy as np
from environs import Env
from validation_utils import (
    get_unique_vals,
    initialize_validation_output_dict,
    write_out_to_json,
    write_out_to_csv,
    create_dataframe,
)

# ----------------------
# Functions
# ----------------------


def validate_schema_fips(group_col, group_values, df, feature, output_dict):
    """ Validate the schema for fips

    Input:
        group_col (str): Name of column to group results by.
        group_values (str): Names of specific groups in group_col.
        df (pd.DataFrame): Pandas DataFrame containing the data.
        feature (str): Names of the feature (column) of interest.
        output_dict (dict): Dictionary containing schema validation results and metadata.
                            Will be written as JSON file at the end.

    Returns:
        output_dict (dict): The updated output dictionary.

    Assumptions for fips:
    - Values are floats
    - Values are non-negative
    """
    for group_value in group_values:
        # ---------------------------------------------------
        # Get unique values in the column (feature) of interest
        # ---------------------------------------------------
        feature_values = get_unique_vals(df, feature, group_col, group_value)

        # Initialize variable to keep track of schema validity
        status = "valid"

        # Validate feature schema
        for val in feature_values:

            # Continue this loop until you hit an invalid
            # This prevents from only saving the last value's status
            if status == "valid":

                # Check if value is a float
                if type(val) in [float, np.float64]:
                    # Check if non-negative
                    if val < 0:
                        status = "invalid: value must be non-negative"
                    else:
                        status = "valid"
                elif type(val) == int:
                    if val < 0:
                        status = "invalid: value must be non-negative"
                    else:
                        status = "valid: warning value is int but expected float"
                else:
                    status = "invalid: value not a float"

            # Update dictionary
            output_dict["schema_validation"][group_col][group_value].update(
                {feature: {"status": status, "n_vals": len(feature_values)}}
            )

    return output_dict


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
        "-p",
        "--dataPath",
        type=str,
        required=True,
        help="Path to data in .csv format (filepath or URL)",
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
    env = Env()
    env.read_env()

    # Assign arguments to variables
    modelID = args.modelID
    data_path = args.dataPath
    group_col = args.group_col

    with mlflow.start_run():
        # ------------------------------------
        # 1. Load in data
        # ------------------------------------

        df = pd.read_csv(data_path)

        # ------------------------------------
        # 2. Specify what feature to retrieve from the specified table
        # ------------------------------------

        feature = "fips"

        # ------------------------------------
        # 3. Initialize output dictionary
        # ------------------------------------
        # Set arguments
        if group_col == "":
            group_values = [""]
        else:
            group_values = list(df[group_col].unique())

        # Initialize
        output_dict = initialize_validation_output_dict(
            modelID, feature, group_col, group_values
        )

        # ------------------------------------
        # 4. Update output dictionary
        # ------------------------------------
        output_dict = validate_schema_fips(
            group_col=group_col,
            group_values=group_values,
            df=df,
            feature=feature,
            output_dict=output_dict,
        )
        print(
            "Schema validation check for {0} complete for all groups.".format(feature)
        )

        # ------------------------------------
        # 5. Output dictionary to JSON file
        # ------------------------------------
        out_file_name = "model-{0}_schema_validation_results.json".format(modelID)
        write_out_to_json(out_file_name, output_dict)
        mlflow.log_artifact(out_file_name)

        # ------------------------------------
        # 6. Write to SQL Server Tables
        # ------------------------------------
        schema_drift_df = create_dataframe(
            output_dict["schema_validation"], group_col, group_values, modelID,
        )

        csv_name = "model-{0}_schema_validation_results.csv".format(modelID)
        write_out_to_csv(csv_name, schema_drift_df)
        mlflow.log_artifact(csv_name)

