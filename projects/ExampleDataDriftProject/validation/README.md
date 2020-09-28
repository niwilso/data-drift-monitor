# Readme - Validation Scripts

The first portion of data drift monitoring involves validating input feature schema. The Python scripts in `./model_input/` check the schema of the various input features fed into the benchmark mortality model.

Specifically, individual validate_[featureName].py scripts are run. These scripts check the schema of the unique values present in the feature of interest. Status on whether all the values are valid or invalid is written out to a results json and results csv file (for easy writing to a SQL table). The validity status message will provide additional information if invalid (e.g., "invalid: values outside of expected range").

The example scripts here are specific to the [New York Times COVID-19 dataset](https://github.com/nytimes/covid-19-data) by [county](https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv).

We have included example results files [../example_schema_validation_results.csv](../example_schema_validation_results.csv) and [../example_schema_validation_results.json](../example_schema_validation_results.json).

To perform schema validation on your own dataset, please create the appropriate validate_[featureName].py files and update [../../MLProject](../../MLProject) to call the appropriate validation scripts.

For a detailed list of what criteria are evaluated for each feature, please see the readme within the respective folder (e.g., `./model_input`).
