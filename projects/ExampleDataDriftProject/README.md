# README

This example project demonstrates how data drift monitoring was performed for the Philips PCA Phase II engagement, using MLFlow on Databricks. In this example, we adapted the code to be more generalizable and work with an open dataset.

Pipeline variables from the Azure DevOps pipeline are read as parameters in `[MLFlow entry point]/parameters.json.j2`. These parameters are then passed into the Python script calls in `MLProject`.

Note, some functions have been adapted to read in a .csv file for this example project. In the original code, data was read in from and written to SQL tables.

## Data Drift Overview

In the Philips engagement, we were particularly interested in monitoring two types of data drift.

1. **Schema drift**. Change in the format/schema of the data. For example, one ICU changes to a new machine for recording blood pressure, and instead of outputting diastolic and systolic as two separate floats as expected, it outputs two strings (e.g., "120s", "80d"). This unexpected format change could lead the model to fail.
2. **Distribution drift**. Change in the overall distribution of the data. For example, a piece of equipment begins to malfunction and always report blood pressure as 20 points higher than usual.

Schema validation for each feature is unique and required a unique `validation/model_input/validate_[feature].py` file.

For distribution drift, we compare a **target** distribution to a **baseline** distribution. Our target is the set of data we want to monitor drift for (e.g., the most recent quarter of data for a specific hospital). Our baseline is the set of data we make our target comparison against (e.g., historical data from the same hospital). Drift is calculated per feature.

Results for schema validation and distribution drift were written to SQL tables in their database.

### Schema Validation

In the Philips PCA Phase II engagement, we performed schema validation for a select few model input features. In this example, we perform schema validation for all three features of interest in the [New York Times COVID-19 dataset](https://github.com/nytimes/covid-19-data). More details in the [Schema Validation readme](validation/README.md).

### Distribution Drift

Distribution drift was calculated for all input features used in the benchmark mortality model using the Python library [alibi-detect](https://docs.seldon.io/projects/alibi-detect/en/latest/methods/ksdrift.html). More details in the [Distribution Drift readme](distribution/README.md).

## Example Data

In this example project, we use the New York Times [public COVID-19 dataset](https://github.com/nytimes/covid-19-data). The data by county as of 2020-08-27 was pulled and saved into `data/covid_sample_data_US_counties.csv`. For more details, see the [data readme](data/README.md).

## Pipeline Creation

The data drift monitoring pipeline will need to be created in Azure DevOps using [`/.azure_pipelines/data_drift.yml`](../../.azure_pipelines/data_drift.yml). The following pipeline variables will need to be added to the pipeline.

| Variable Name    | Default Value        | Description                                                                                                                |
|------------------|----------------------|----------------------------------------------------------------------------------------------------------------------------|
| BASELINE_END     | 2020-05-31           | End date of the baseline period in YYYY-MM-DD format.                                                                      |
| BASELINE_START   | 2020-01-21           | Start date of the baseline period in YYYY-MM-DD format.                                                                    |
| DATA_PATH        | `https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv`   | Location of data (either local path or URL).                 |
| DATETIME_COL     | date                 | Name of column containing datetime information.                                                                            |
| FEATURES         | fips,cases,deaths    | List of features to perform schema validation for, separated by commas with no spaces.                                     |
| GROUP_COL        | state                | Name of column to group results by.                                                                                        |
| MODEL_ID         | 1                    | Appropriate model ID number associated with the data we are performing drift monitoring for (see mon.vrefModel).           |
| OUT_FILE_NAME    | results.json         | Name of .json file storing results.                                                                                        |
| P_VAL            | 0.05                 | Threshold value for p-values in distribution drift monitoring. Values below the threshold will be labelled as significant. |
| TARGET_END       | 2019-08-27           | End date of the target period in YYYY-MM-DD format.                                                                        |
| TARGET_START     | 2019-08-01           | Start date of the target period in YYYY-MM-DD format.                                                                      |

Once the pipeline is triggered in Azure DevOps, see the "Execute Data Drift Project (schema validation)" and "Execute Data Drift Project (distribution drift)" steps to click a link to the Databricks MLFlow job run page. On this run page, you can see what is being written to standard out / standard error. Note, the PyArrow error printed to standard error can be ignored as it does not affect any of the processes. At the top of the run page, you may see job status and run time.
