""" Calculate distribution drift for all specified features
"""

import pandas as pd
import numpy as np
import datetime
import argparse
import decimal
import mlflow
import os
import sys
from environs import Env

# ----------------------
# Import Common Functions
# ----------------------
sys.path.append(os.getcwd())
from common.common_utils import format_arg_features  # noqa: E402

# ----------------------
# Functions
# ----------------------


def get_baseline_target_range(
    df,
    datetime_col,
    baseline_start="",
    baseline_end="",
    target_start="",
    target_end="",
):
    """ If not provided, find default baseline and target ranges.

    Set baseline as all data up to 90 days prior, and target as the most recent 90 days.
    Note that validation of these date ranges happens in a separate function (validate_datetime_range()) later.

    Input:
        df (pd.DataFrame): Pandas DataFrame containing the data.
        datetime_col (str): Name of column in df containing datetime information.
        baseline_start (str): Empty string or baseline start date in YYYY-MM-DD format (e.g., '2015-01-01').
        baseline_end (str): Empty string or baseline end date in YYYY-MM-DD format (e.g., '2018-01-01').
        target_start (str): Empty string or target start date in YYYY-MM-DD format (e.g., '2018-01-01').
        target_end (str): Empty string or target end date in YYYY-MM-DD format (e.g., '2020-01-01').

    Returns:
        baseline_start (str): Baseline start date in YYYY-MM-DD format (e.g., '2015-01-01').
        baseline_end (str): Baseline end date in YYYY-MM-DD format (e.g., '2018-01-01').
        target_start (str): Target start date in YYYY-MM-DD format (e.g., '2018-01-01').
        target_end (str): Target end date in YYYY-MM-DD format (e.g., '2020-01-01').
    """

    # Get min and max datetime range
    dates = list(df[datetime_col].apply(pd.to_datetime))

    range_min = np.min(dates)
    range_max = np.max(dates)

    # Assign start and end dates if not specified
    if baseline_start == "":
        baseline_start = range_min
        baseline_start = str(baseline_start).rsplit(" ")[0]
        print("baseline_start being set to {0}".format(baseline_start))
    else:
        print("baseline_start read in as {0}".format(baseline_start))

    if baseline_end == "":
        baseline_end = range_max - datetime.timedelta(days=90)
        baseline_end = str(baseline_end).rsplit(" ")[0]
        print("baseline_end being set to {0}".format(baseline_end))
    else:
        print("baseline_end read in as {0}".format(baseline_end))

    if target_start == "":
        target_start = range_max - datetime.timedelta(days=90)
        target_start = str(target_start).rsplit(" ")[0]
        print("target_start being set to {0}".format(target_start))
    else:
        print("target_start read in as {0}".format(target_start))

    if target_end == "":
        target_end = range_max
        target_end = str(target_end).rsplit(" ")[0]
        print("target_end being set to {0}".format(target_end))
    else:
        print("target_end read in as {0}".format(target_end))

    return baseline_start, baseline_end, target_start, target_end


def validate_datetime_range(
    start, end, df, datetime_col, group_col, group_value, verbose=True
):
    """ Ensure the datetime range works for the SQL table.

    Input:
        start (str or datetime.datetime): Starting datetime (e.g., 2011-02-22).
        end (str or datetime.datetime): Ending datetime (e.g., 2011-02-23).
        df (pd.DataFrame): Pandas DataFrame containing the data.
        datetime_col (str): Name of column in df containing datetime information.
        group_col (str): Name of column to group results by.
        group_value (str): Name of a specific group in group_col.
        verbose (boolean): Whether to print status and table datetime range.

    Returns:
        datetime_status (boolean): Whether the input start and end datetimes are valid.
        range_min (datetime.datetime): Earliest datetime in the table.
        range_max (datetime.datetime): Most recent datetime in the table.
    """
    # Set default as invalid
    datetime_status = False

    # Convert to datetime if input is string
    if type(start) == str:
        start = datetime.datetime.strptime(start, "%Y-%m-%d")

    if type(end) == str:
        end = datetime.datetime.strptime(end, "%Y-%m-%d")

    # Get min and max datetime range
    if group_col == "":
        dates = list(df[datetime_col].apply(pd.to_datetime))
    else:
        dates = list(
            df.loc[df[group_col] == group_value][datetime_col].apply(pd.to_datetime)
        )

    range_min = np.min(dates)
    range_max = np.max(dates)

    if verbose is True:
        print("datetime range: {0} to {1} ".format(range_min, range_max))

    # Check that start is not after max
    if start < range_max:
        # Check that end is not before min
        if end > range_min:
            # Check that end is after start
            if start < end:
                datetime_status = True

    return datetime_status, range_min, range_max


def initialize_df():
    """ Initialize the dictionary that will store results.

    Returns:
        df (dataframe)
    """

    df = pd.DataFrame(
        columns=[
            "group_col",
            "group_value",
            "feature",
            "pValue",
            "isSignificantDrift",
            "baselineSamples",
            "baselineNullValues",
            "baselineRemoved",
            "baselineValues",
            "baselineValueCounts",
            "baselineValuePercentages",
            "targetSamples",
            "targetNullValues",
            "targetRemoved",
            "targetValues",
            "targetValueCounts",
            "targetValuePercentages",
        ]
    )
    return df


def retrieve_data(
    features, df, datetime_col, group_col, group_value, start_datetime, end_datetime,
):
    """ Retrieve data for one feature from a specific group over a specified datetime range.

    Input:
        features (list of str): Names of the features (columns) of interest.
        df (pd.DataFrame): Pandas DataFrame containing data.
        datetime_col (str): Name of column in df containing datetime information.
        group_col (str): Name of column to group results by.
        group_value (str): Name of a specific group in group_col.
        start_datetime (str): Starting datetime (e.g., 2011-02-22).
        end_datetime (str): Ending datetime (e.g., 2011-02-23).

    Returns:
        df_out (pd.DataFrame): Pandas DataFrame containing the feature data and associated datetime.
    """
    if group_col == "":
        df_out = df
        df_out[datetime_col] = list(df_out[datetime_col].apply(pd.to_datetime))
    else:
        df_out = df.loc[df[group_col] == group_value]
        df_out[datetime_col] = list(
            df_out.loc[df[group_col] == group_value][datetime_col].apply(pd.to_datetime)
        )
    df_out = df_out.loc[df_out[datetime_col] >= start_datetime]
    df_out = df_out.loc[df_out[datetime_col] <= end_datetime]
    df_out = df_out[features]

    return df_out


def rank_feature_drift(preds, feature_names, p_val=0.05):
    """ Rank likely drift contribution by feature.

    Inputs:
        preds (dict): dfdf.
        feature_names (list of str): List of feature names.
        p_val (float): p-value threshold being used in prediction.

    Returns:
        drift_by_feature (pd.DataFrame): Ranked list of likely contributors.
    """

    vals = preds["data"]["p_val"]

    # First check the number of features and prediction p-values match
    try:
        assert len(feature_names) == len(vals)
    except AssertionError:
        print("Ensure prediction is being run with all features.")

    # Sort from lowest to highest p-value
    # Lowest p-value indicates greatest confidence in distribution difference
    sort_index = np.argsort(vals)  # argsort is in ascending order by default
    features_sorted = [feature_names[idx] for idx in sort_index]
    vals_sorted = vals[sort_index]

    # Drift by feature
    drift_by_feature = pd.DataFrame(
        dict(
            {
                "feature": features_sorted,
                "p_val": vals_sorted,
                "is_significant_drift": vals_sorted < p_val,
            }
        )
    )

    return drift_by_feature


def detect_drift_by_ID(
    group_col,
    group_values,
    df,
    datetime_col,
    features,
    baseline_start,
    baseline_end,
    target_start,
    target_end,
    output_df,
    p_val,
):
    """ Detect drift for each feature for a given ID.

    Input:
        group_col (str): Name of column to group results by.
        group_value (str): Name of a specific group in group_col.
        df (pd.DataFrame): Pandas DataFrame containing the data.
        datetime_col (str): Name of column in df containing datetime information.
        features (list of str): Names of the features (columns) of interest.
        baseline_start (str): Baseline start date in YYYY-MM-DD format (e.g., '2015-01-01').
        baseline_end (str): Baseline end date in YYYY-MM-DD format (e.g., '2018-01-01').
        target_start (str): Target start date in YYYY-MM-DD format (e.g., '2018-01-01').
        target_end (str): Target end date in YYYY-MM-DD format (e.g., '2020-01-01').
        output_df (pd.DataFrame): DataFrame containing drift results.
        p_val (float): p-value to use for determining drift significance.

    Returns:
        output_df (pd.DataFrame): The updated output DataFrame.
    """
    # Import inside function to avoid import error when doing unit tests
    from alibi_detect.cd import KSDrift

    for group_value in group_values:
        # ---------------------------------------------------
        # Retrieve data
        # ---------------------------------------------------
        # Ensure date range is valid for current ID
        baseline_datetime_status, _, _ = validate_datetime_range(
            baseline_start, baseline_end, df, datetime_col, group_col, group_value,
        )
        target_datetime_status, _, _ = validate_datetime_range(
            target_start, target_end, df, datetime_col, group_col, group_value,
        )

        try:
            assert baseline_datetime_status is True
            assert target_datetime_status is True

            # Retrieve data for baseline and target
            df_baseline = retrieve_data(
                features,
                df,
                datetime_col,
                group_col,
                group_value,
                baseline_start,
                baseline_end,
            )

            df_target = retrieve_data(
                features,
                df,
                datetime_col,
                group_col,
                group_value,
                target_start,
                target_end,
            )
            print("len(df): {0}".format(len(df)))
            print("len(df_baseline): {0}".format(len(df_baseline)))
            print("len(df_target): {0}".format(len(df_target)))

            # ---------------------------------------------------
            # Drift detection
            # ---------------------------------------------------
            X_baseline = df_baseline[features].dropna().to_numpy()
            X_target = df_target[features].dropna().to_numpy()

            if X_target.size == 0:
                return output_df

            # Initialize drift monitor using Kolmogorov-Smirnov test
            # https://docs.seldon.io/projects/alibi-detect/en/latest/methods/ksdrift.html
            cd = KSDrift(p_val=p_val, X_ref=X_baseline, alternative="two-sided")

            # Get ranked list of feature by drift (ranked by p-value)
            preds_h0 = cd.predict(X_target, return_p_val=True)
            drift_by_feature = rank_feature_drift(preds_h0, features)

            # ---------------------------------------------------
            # Update output dataframe
            # ---------------------------------------------------
            len_baseline = len(df_baseline)
            len_target = len(df_target)

            for feature in features:
                # loop through each feature and generate means for baseline and target
                # function to generate mean statistics

                # loop through each feature and generate means for baseline and target
                # only produce statistics for string features, assign nan for numeric features
                featurevalues_base = df_baseline[feature].dropna().to_numpy()
                if type(featurevalues_base[0]) == str:
                    uniqueValue_base, valueCount_base = np.unique(
                        featurevalues_base, return_counts=True
                    )
                    valuePct_base = valueCount_base * 100 / len(featurevalues_base)

                    # Convert from np.ndarray to list
                    uniqueValue_base = list(uniqueValue_base)
                    valueCount_base = list(valueCount_base)
                    valuePct_base = list(valuePct_base)
                else:
                    uniqueValue_base = list()
                    valueCount_base = list()
                    valuePct_base = list()

                featurevalues_tar = df_target[feature].dropna().to_numpy()
                if type(featurevalues_tar[0]) == str:
                    featurevalues_tar = df_target[feature].dropna().to_numpy()
                    uniqueValue_tar, valueCount_tar = np.unique(
                        featurevalues_tar, return_counts=True
                    )
                    valuePct_tar = valueCount_tar * 100 / len(featurevalues_tar)

                    # Convert from np.ndarray to list
                    uniqueValue_tar = list(uniqueValue_tar)
                    valueCount_tar = list(valueCount_tar)
                    valuePct_tar = list(valuePct_tar)
                else:
                    uniqueValue_tar = list()
                    valueCount_tar = list()
                    valuePct_tar = list()

                # manually add values that are only in one of the comparison samples and set count/pct to 0
                for value in uniqueValue_tar:
                    valueCount_base.append(
                        0
                    ) if value not in uniqueValue_base else valueCount_base
                    valuePct_base.append(
                        0
                    ) if value not in uniqueValue_base else valuePct_base
                    uniqueValue_base.append(
                        value
                    ) if value not in uniqueValue_base else uniqueValue_base
                for value in uniqueValue_base:
                    valueCount_tar.append(
                        0
                    ) if value not in uniqueValue_tar else valueCount_tar
                    valuePct_tar.append(
                        0
                    ) if value not in uniqueValue_tar else valuePct_tar
                    uniqueValue_tar.append(
                        value
                    ) if value not in uniqueValue_tar else uniqueValue_tar

                row = {}
                row["group_col"] = group_col
                row["group_value"] = group_value
                row["feature"] = feature
                row["pValue"] = float(
                    drift_by_feature.loc[drift_by_feature["feature"] == feature][
                        "p_val"
                    ].values
                )
                row["isSignificantDrift"] = bool(
                    drift_by_feature.loc[drift_by_feature["feature"] == feature][
                        "is_significant_drift"
                    ].values
                )
                row["baselineSamples"] = len_baseline
                row["baselineNullValues"] = df_baseline[feature].isna().sum()
                row["baselineRemoved"] = len_baseline - len(df_baseline.dropna())
                row["baselineValues"] = str(uniqueValue_base)
                row["baselineValueCounts"] = str(valueCount_base)
                row["baselineValuePercentages"] = str(valuePct_base)
                row["targetSamples"] = len_target
                row["targetNullValues"] = df_target[feature].isna().sum()
                row["targetRemoved"] = len_target - len(df_target.dropna())
                row["targetValues"] = str(uniqueValue_tar)
                row["targetValueCounts"] = str(valueCount_tar)
                row["targetValuePercentages"] = str(valuePct_tar)

                output_df = output_df.append(row, ignore_index=True)

            # Print progress for now
            print("{0}: {1} done".format(group_col, group_value))

        except AssertionError:
            print(
                "Baseline date range {0} to {1} or target date range {2} to {3} invalid for {4}: {5}".format(
                    baseline_start,
                    baseline_end,
                    target_start,
                    target_end,
                    group_col,
                    group_value,
                )
            )
            pass

    return output_df


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
        "-x",
        "--dataPath",
        type=str,
        required=True,
        help="Path to data in .csv format (filepath or URL)",
    )
    parser.add_argument(
        "-f",
        "--features",
        type=str,
        required=True,
        help="Comma separated list of features to monitor (e.g., featureName1,featureName2)",
    )
    parser.add_argument(
        "-t",
        "--datetimeCol",
        type=str,
        required=True,
        help="Name of column in data that contains datetime information",
    )
    parser.add_argument(
        "-g",
        "--group_col",
        type=str,
        required=False,
        default="",
        help="Name of column in data to group by.",
    )
    parser.add_argument(
        "-a",
        "--baselineStart",
        type=str,
        required=False,
        default="",
        help="Start date of baseline period in YYYY-MM-dd format (e.g., 2011-03-01)",
    )
    parser.add_argument(
        "-b",
        "--baselineEnd",
        type=str,
        required=False,
        default="",
        help="End date of baseline period in YYYY-MM-dd format (e.g., 2018-02-09)",
    )
    parser.add_argument(
        "-c",
        "--targetStart",
        type=str,
        required=False,
        default="",
        help="Start date of target period in YYYY-MM-dd format (e.g., 2020-01-01)",
    )
    parser.add_argument(
        "-d",
        "--targetEnd",
        type=str,
        required=False,
        default="",
        help="End date of target period in YYYY-MM-dd format (e.g., 2020-03-01)",
    )
    parser.add_argument(
        "-p",
        "--pValue",
        type=float,
        required=False,
        default=0.05,
        help="Alpha value that will be set as threshold for determining statistical significance (e.g., 0.05)",
    )

    args = parser.parse_args()
    env = Env()
    env.read_env()

    # Assign arguments to variables
    modelID = args.modelID
    data_path = args.dataPath
    features = format_arg_features(args.features)
    datetime_col = args.datetimeCol
    group_col = args.group_col
    baseline_start = args.baselineStart
    baseline_end = args.baselineEnd
    target_start = args.targetStart
    target_end = args.targetEnd
    p_val = args.pValue

    with mlflow.start_run():
        # ------------------------------------
        # 1. Load in data
        # ------------------------------------

        df = pd.read_csv(data_path)

        # ------------------------------------
        # 2. Initialize dataframe
        # ------------------------------------

        # Get dates if not specified
        (
            baseline_start,
            baseline_end,
            target_start,
            target_end,
        ) = get_baseline_target_range(
            df, datetime_col, baseline_start, baseline_end, target_start, target_end,
        )

        # Set arguments
        if group_col == "":
            group_values = [""]
        else:
            group_values = list(df[group_col].unique())

        # Initialize
        drift_results_df = initialize_df()

        # ------------------------------------
        # 3. Update output dataframe
        # ------------------------------------
        drift_results_df = detect_drift_by_ID(
            group_col=group_col,
            group_values=group_values,
            df=df,
            datetime_col=datetime_col,
            features=features,
            baseline_start=baseline_start,
            baseline_end=baseline_end,
            target_start=target_start,
            target_end=target_end,
            output_df=drift_results_df,
            p_val=p_val,
        )

        # ------------------------------------
        # 4. Write results
        # ------------------------------------
        results_file_name = "model-{0}_distribution_drift_results.csv".format(modelID)
        drift_results_df.to_csv(results_file_name, index=False, header=True)
        mlflow.log_artifact(results_file_name)

