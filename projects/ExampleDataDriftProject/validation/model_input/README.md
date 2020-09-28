# Readme - Model Input Feature Validation

The scripts within this directory check whether the schema for any model **input features** of interest are valid. The specific validation criteria for each monitored feature are listed below.

## fips

- Value must be a float
- Value must not be non-negative

## cases

- Value must be an integer
- Value must not be non-negative

## deaths

- Value must be an integer
- Value must not be non-negative
  