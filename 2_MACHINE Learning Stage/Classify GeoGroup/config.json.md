# Configuration File (config.json) Documentation

This document explains the parameters in `config.json` used by AncestryGeni.

## Input/Output Settings

- `INPUT_TRAINING_FOLDER`: Directory containing training data files
- `INPUT_TESTING_FOLDER`: Directory containing testing data files
- `INPUT_TRAINING_FILE`: Name of the training data file
- `INPUT_TESTING_FILE`: Name(s) of testing data file(s)

## Data Processing Options

- `MMRF_DATA`: Boolean flag for Multiple Myeloma Research Foundation data format
  - `1`: Remove ancestry codes 3 and 6
  - `0`: Keep all ancestry codes

- `SPLIT_DATA`: Controls data splitting behavior
  - `1`: Split data for main diagonal calculation
  - `0`: No splitting

- `N_SPLITS`: Number of cross-validation splits (default: 10)

## Column Specifications

- `COLS`: Object defining column names
  - `TARGET`: Array containing target column name (e.g., ["Code"])
  - `ANNOT`: Array of annotation column names (e.g., ["Dataset", "Sample", "SampleCode"])

## Ancestry Codes

- 1: White/European
- 2: Black/African
- 3: Hispanic
- 4: Asian
- 6: Other

## Example Usage

For basic analysis:
```json
{
    "INPUT_TRAINING_FOLDER": "./training_data",
    "INPUT_TESTING_FOLDER": "./testing_data",
    "INPUT_TRAINING_FILE": "training.txt",
    "INPUT_TESTING_FILE": ["test.txt"],
    "SPLIT_DATA": 1,
    "MMRF_DATA": 0,
    "N_SPLITS": 10,
    "COLS": {
        "TARGET": ["Code"],
        "ANNOT": ["Dataset", "Sample", "SampleCode"]
    }
}
``` 