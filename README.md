# Clinical Data Drift Monitoring Example

In ["Building a clinical data drift monitoring system with Azure DevOps, Azure Databricks, and MLflow"](https://devblogs.microsoft.com/cse/2020/10/29/building-a-clinical-data-drift-monitoring-system-with-azure-devops-azure-databricks-and-mlflow/), we detail our approach to implementing data drift monitoring of healthcare data for Philips in a Microsoft Commercial Software Engineering (CSE) and Philips collaboration.

This repository contains example code and provides documentation on how to set up a data drift monitoring pipeline in Azure DevOps using the open source [New York Times COVID-19 dataset](https://github.com/nytimes/covid-19-data).

## Where to start

- [How to create a Databricks workspace to run the code](docs/README.md)
- [How to set up the data drift monitoring pipeline](docs/mlops_example_data_drift_project.md)
- [Data drift monitoring pipeline code](.azure_pipelines/data_drift.yml)
- [Overview of the data drift monitoring code](projects/ExampleDataDriftProject/README.md)
