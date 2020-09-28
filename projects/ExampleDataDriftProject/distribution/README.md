# Readme - Distribution Drift

One portion of data drift monitoring involves observing changes in data distribution over time. `calculate_all_drift.py` measures the change in distribution for each feature between a baseline and target time period using the [Kolmogorov-Smirnov two sample tests](https://docs.seldon.io/projects/alibi-detect/en/latest/methods/ksdrift.html).

This distribution drift code should work out-of-the-box for most uses cases.

## Results Structure

We have included an example results file [../example_distribution_drift_results.csv](../example_distribution_drift_results.csv).

The columns baselineValues, baselineValueCounts, baselineValuePercentages, targetValues, targetValueCounts, and targetValuePercentages are all empty in this example as they are meant to contain data for categorical variables.

| Column Name              | Type    | Description                                                                                                         |
|--------------------------|---------|---------------------------------------------------------------------------------------------------------------------|
| group_col                | string  | Name of column used to group results (e.g., "state").                                                               |
| group_value              | string  | Value in group_col (e.g., "Nebraska").                                                                              |
| feature                  | string  | Name of feature that drift detection is being run on (e.g., "cases").                                               |
| pValue                   | float   | Threshold set for determining significance for Kolmogorov-Smirnov test on a given feature.                          |
| isSignificantDrift       | boolean | True or False on whether drift detection on a feature results in a p-value below the pValue threshold.              |
| baselineSamples          | integer | The number of samples present in the baseline.                                                                      |
| baselineNullValues       | integer | The number of null values in the baseline for this specific feature.                                                |
| baselineRemoved          | integer | The number of rows removed in the baseline, based on presence of null in all features.                              |
| baselineValues           | string  | If the feature is categorical, a list of all values present in the baseline (e.g., [yes, no, maybe])                |
| baselineValueCounts      | string  | If the feature is categorical, a list of counts for all values present in the baseline (e.g., [60, 30, 10])         |
| baselineValuePercentages | string  | If the feature is categorical, a list of proportions for all values present in the baseline (e.g., [0.6, 0.3, 0.1]) |
| targetNullValues         | integer | The number of null values in the target for this specific feature.                                                  |
| targetRemoved            | integer | The number of rows removed in the target, based on presence of null in all features.                                |
| targetValues             | string  | If the feature is categorical, a list of all values present in the target (e.g., [yes, no, maybe])                  |
| targetValueCounts        | string  | If the feature is categorical, a list of counts for all values present in the target (e.g., [60, 30, 10])           |
| targetValuePercentages   | string  | If the feature is categorical, a list of proportions for all values present in the target (e.g., [0.6, 0.3, 0.1])   |
