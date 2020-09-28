""" Test ../distribution/calculate_all_drift.py
"""

import sys
import os
import pandas as pd
import numpy as np
import datetime
import decimal
import pytest

sys.path.append(os.getcwd())
from distribution.calculate_all_drift import (  # noqa: E402
    get_baseline_target_range,
    validate_datetime_range,
    initialize_df,
    retrieve_data,
    rank_feature_drift,
)


@pytest.fixture
def test_df(scope="module"):
    df1 = pd.DataFrame()
    df1["dxGroup"] = [
        "InfectionGenitourinary",
        "InfectionGenitourinary",
        "CHF",
        "CHF",
        "Aneurysm",
        "ValveReplacement",
        "ValveReplacement",
        "ACS",
        "Seizures (primary-no structural brain disease)",
        "Seizures (primary-no structural brain disease)",
    ]
    df1["avgHGB"] = [9.7, 9.7, 11.7, 11.7, 11.8, 12.45, 12.45, 13.3, 11.9, 11.9]
    df1["gcsTotalLast"] = ["15", "15", "15", "15", "15", "10", "10", "15", "11", "11"]
    df1["healthSystemID"] = [
        "exampleHealthSystem01",
        "exampleHealthSystem01",
        "exampleHealthSystem01",
        "exampleHealthSystem01",
        "exampleHealthSystem01",
        "exampleHealthSystem01",
        "exampleHealthSystem01",
        "exampleHealthSystem01",
        "exampleHealthSystem01",
        "exampleHealthSystem01",
    ]
    df1["hospitalID"] = [
        "exampleHospital01",
        "exampleHospital01",
        "exampleHospital02",
        "exampleHospital02",
        "exampleHospital03",
        "exampleHospital03",
        "exampleHospital03",
        "exampleHospital03",
        "exampleHospital01",
        "exampleHospital01",
    ]
    df1["hospitalDischargeDate"] = [
        "2017-04-04",
        "2017-04-04",
        "2017-10-20",
        "2017-10-20",
        "2008-08-12",
        "2013-07-23",
        "2013-07-23",
        "2012-07-4",
        "2015-11-10",
        "2015-11-10",
    ]

    return df1


def test_get_baseline_target_range(test_df):
    # Arrange

    # Act
    baseline_start, baseline_end, target_start, target_end = get_baseline_target_range(
        test_df, "hospitalDischargeDate"
    )

    # Assert
    assert baseline_start == "2008-08-12"
    assert target_end == "2017-10-20"


def test_validate_datetime_range_valid(test_df):
    # Arrange
    start = "2016-01-01"
    end = "2016-12-31"
    datetime_col = "hospitalDischargeDate"
    group_col = "hospitalID"
    group_value = "exampleHospital01"

    # Act
    datetime_status, range_min, range_max = validate_datetime_range(
        start, end, test_df, datetime_col, group_col, group_value, verbose=False
    )

    # Assert
    assert datetime_status == True
    assert range_min == pd.Timestamp("2015-11-10 00:00:00")
    assert range_max == pd.Timestamp("2017-04-04 00:00:00")


def test_validate_datetime_range_invalid(test_df):
    # Arrange
    start = "3215-04-12"
    end = "1995-03-13"
    datetime_col = "hospitalDischargeDate"
    group_col = "hospitalID"
    group_value = "exampleHospital01"

    # Act
    datetime_status, range_min, range_max = validate_datetime_range(
        start, end, test_df, datetime_col, group_col, group_value, verbose=False
    )

    # Assert
    assert datetime_status == False
    assert range_min == pd.Timestamp("2015-11-10 00:00:00")
    assert range_max == pd.Timestamp("2017-04-04 00:00:00")


def test_initialize_df():
    # Arrange

    # Act
    df = initialize_df()

    # Assert
    assert type(df) == pd.DataFrame


def test_retrieve_data(test_df):
    # Arrange
    start_datetime = "2015-11-10"
    end_datetime = "2017-04-04"
    datetime_col = "hospitalDischargeDate"
    group_col = "hospitalID"
    group_value = "exampleHospital01"
    features = [
        "dxGroup",
        "avgHGB",
        "gcsTotalLast",
        "healthSystemID",
        "hospitalID",
        "hospitalDischargeDate",
    ]

    # Act
    df_out = retrieve_data(
        features,
        test_df,
        datetime_col,
        group_col,
        group_value,
        start_datetime,
        end_datetime,
    )

    # Assert
    assert len(df_out) == 4


# ----------------------------------------------------------------------------------------------
# Test various conditions for rank_feature_drift
# Note: We are not using @pytest.mark.parameterize because the assertions are different by case
# ----------------------------------------------------------------------------------------------


def test_rank_feature_drift_one_feature():
    # Arrange
    preds = {
        "data": {
            "batch_score": None,
            "feature_score": None,
            "is_drift": 0,
            "p_val": np.array([0.0000142], dtype=np.float32),
        },
        "meta": {"name": "KSDrift", "detector_type": "offline", "data_type": None},
    }
    feature_names = ["dxGroup"]
    p_val = 0.05

    # Act
    drift_by_feature = rank_feature_drift(preds, feature_names, p_val)

    # Assert
    assert drift_by_feature["feature"][0] == "dxGroup"
    assert abs(drift_by_feature["p_val"][0] - 0.0000142) < 0.0000001
    assert drift_by_feature["is_significant_drift"][0] == True  # noqa: E712
    assert len(drift_by_feature) == 1


def test_rank_feature_drift_two_features():
    # Arrange
    preds = {
        "data": {
            "batch_score": None,
            "feature_score": None,
            "is_drift": 0,
            "p_val": np.array([0.7499942, 0.0000142], dtype=np.float32),
        },
        "meta": {"name": "KSDrift", "detector_type": "offline", "data_type": None},
    }
    feature_names = ["gcsTotalLast", "dxGroup"]
    p_val = 0.05

    # Act
    drift_by_feature = rank_feature_drift(preds, feature_names, p_val)

    # Assert
    assert drift_by_feature["feature"][0] == "dxGroup"
    assert abs(drift_by_feature["p_val"][0] - 0.0000142) < 0.0000001
    assert drift_by_feature["is_significant_drift"][0] == True  # noqa: E712
    assert len(drift_by_feature) == 2


def test_rank_feature_drift_five_features():
    # Arrange
    preds = {
        "data": {
            "batch_score": None,
            "feature_score": None,
            "is_drift": 0,
            "p_val": np.array(
                [0.7499942, 0.0000142, 0.3214539, 0.0082934, 0.0000062],
                dtype=np.float32,
            ),
        },
        "meta": {"name": "KSDrift", "detector_type": "offline", "data_type": None},
    }
    feature_names = ["gcsTotalLast", "dxGroup", "avgHGB", "bmi", "avgSodium"]
    p_val = 0.05

    # Act
    drift_by_feature = rank_feature_drift(preds, feature_names, p_val)

    # Assert
    assert drift_by_feature["feature"][0] == "avgSodium"
    assert abs(drift_by_feature["p_val"][0] - 0.0000062) < 0.0000001
    assert drift_by_feature["is_significant_drift"][0] == True  # noqa: E712
    assert len(drift_by_feature) == 5


@pytest.mark.skip(reason="Relied on SQL table data")
def test_detect_drift_by_ID():
    print("Skip test_detect_drift_by_ID")
