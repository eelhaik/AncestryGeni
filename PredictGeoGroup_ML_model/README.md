# PredictGeoGroup ML Model Documentation

## Overview
PredictGeoGroup is a machine learning-based tool designed to predict geographic ancestry groups based on genetic data. The pipeline includes two main scripts: `PredictGeoGroup1.py` for initial continental ancestry prediction and `PredictGeoGroup2.py` for detailed geographic prediction with probability analysis.

## Repository Structure
```
PredictGeoGroup/
├── AnalyzeVEPFile.py                 # Script for analyzing variant effect prediction (VEP) files
├── comparing_models.ipynb            # Jupyter notebook for comparing different models
├── config.json                       # Main configuration file
├── config_CP.json                    # Configuration for CP-specific settings
├── config_Modern.json                # Configuration for modern datasets
├── FilterPFile.py                    # Script for filtering P files
├── module_model_executor.py          # Module for executing machine learning models
├── module_preprocessor.py            # Module for data preprocessing
├── PredictGeoGroup1.py               # First stage: Continental ancestry prediction
├── PredictGeoGroup2.py               # Second stage: Detailed geographic prediction
└── tuning_and_vis/                   # Directory containing visualization and tuning scripts
    ├── lda_performance_viz.py        # Script for visualizing LDA performance
    └── tune_lda_parameters.py        # Script for tuning hyperparameters of LDA models
```

## Main Scripts

### PredictGeoGroup1.py
- First stage of the pipeline
- Assigns individuals to continental ancestry groups
- Generates confusion matrix for performance evaluation
- Provides initial ancestry estimation

### PredictGeoGroup2.py
- Second stage of the pipeline
- Provides detailed interpretation of ancestry predictions
- Reports top-1 and top-2 classification probabilities
- Identifies borderline cases
- Generates comprehensive visualizations and reports

## Supporting Modules
- **`module_preprocessor.py`**: Handles data preprocessing, feature engineering, and normalization
- **`module_model_executor.py`**: Manages machine learning model training, evaluation, and execution
- **`FilterPFile.py`**: Filters and processes genetic data files
- **`AnalyzeVEPFile.py`**: Analyzes variant effect prediction (VEP) results
- **`lda_performance_viz.py`**: Visualizes performance metrics of LDA models

## Model Comparison & Tuning
- **`comparing_models.ipynb`**: Jupyter notebook for comparing different ML models
- **`tune_lda_parameters.py`**: Fine-tunes hyperparameters for LDA models

## Configuration Files
- **`config.json`**: Main configuration file specifying paths, data sources, and parameters
- **`config_CP.json` & `config_Modern.json`**: Alternative configurations for different datasets

## Output & Results
- **Model files**: Saved in `./ML_models/best_model.pkl`
- **Evaluation metrics**: Stored in `best_performance_metrics.xlsx`
- **Results and visualizations**: Saved in `./ML_results/`
- **Confusion matrices**: Generated for both stages
- **Probability reports**: Top-1 and top-2 classification probabilities

## Usage
1. Ensure the required dependencies are installed
2. Modify `config.json` to specify data sources and parameters
3. Run `PredictGeoGroup1.py` for initial continental prediction:
   ```bash
   python PredictGeoGroup1.py
   ```
4. Run `PredictGeoGroup2.py` for detailed geographic prediction:
   ```bash
   python PredictGeoGroup2.py
   ```
5. Analyze results in `./ML_results/`
6. Use `comparing_models.ipynb` to assess model performance
7. Tune hyperparameters using `tune_lda_parameters.py` if needed

## Dependencies
- Python 3.x
- NumPy
- Pandas
- Scikit-learn
- Joblib
- CommentJSON
- Logging

## Contact
For inquiries or contributions, feel free to reach out or open an issue in the repository.

## Configuration Files

### 1. config.json
Controls the ML model's behavior and data processing:

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

#### Parameters Explained:
- **Input/Output Settings**
  - `INPUT_TRAINING_FOLDER`: Directory containing training data
  - `INPUT_TESTING_FOLDER`: Directory containing test data
  - `INPUT_TRAINING_FILE`: Training data filename
  - `INPUT_TESTING_FILE`: Array of test data filenames

- **Processing Options**
  - `MMRF_DATA`: Toggle MMRF data handling (0/1)
  - `SPLIT_DATA`: Enable data splitting (0/1)
  - `N_SPLITS`: Number of cross-validation splits

- **Column Specifications**
  - `COLS.TARGET`: Target column for prediction
  - `COLS.ANNOT`: Annotation columns

### 2. Parameters.txt
Controls pipeline execution and data flow:

```
ADMIXTURE_DIR=/path/to/admixture
INPUT_DIR=/path/to/vcf/files
OUTPUT_DIR=/path/to/output
OUTPUT_DIR_1KG=/path/to/1kg/output
OUTPUT_DIR_FINAL=/path/to/final/output
OUTPUT_ADMIXTURE_DIR=/path/to/admixture/output
OUTPUT_FILE_TABLE=ancestry_counts.txt
OUTPUT_FILE=snp_counts.txt
DB_NAME=my_dataset
NUM_OF_LINES=1
```

#### Parameters Explained:
- **Directory Settings**
  - `ADMIXTURE_DIR`: ADMIXTURE software location
  - `INPUT_DIR`: VCF files directory
  - `OUTPUT_DIR`: Main results directory
  - `OUTPUT_DIR_1KG`: 1000 Genomes output
  - `OUTPUT_DIR_FINAL`: Final results location
  - `OUTPUT_ADMIXTURE_DIR`: ADMIXTURE analysis directory

- **Output Files**
  - `OUTPUT_FILE_TABLE`: Ancestry counts file
  - `OUTPUT_FILE`: SNP analysis quality control
  - `DB_NAME`: Dataset identifier
  - `NUM_OF_LINES`: Sample line count (1 for GATK, 2 for Somatic)

## Running the Pipeline

1. **Stage 1: Basic Ancestry Prediction**
```bash
python PredictGeoGroup1.py
```
- Assigns continental ancestry groups
- Generates confusion matrix
- Outputs basic predictions

2. **Stage 2: Detailed Analysis**
```bash
python PredictGeoGroup2.py
```
- Analyzes admixed individuals
- Reports classification probabilities
- Creates detailed visualizations

## Output Files

- **Predictions**: `*_with_predictions.csv`
- **Performance**: `output_basic.txt`, `output_detailed.txt`
- **Models**: `best_model.pkl`
- **Visualizations**: Confusion matrices, probability heatmaps

## Performance Metrics

- Accuracy
- F1-score
- Precision/Recall
- Cohen's kappa
- Matthews correlation coefficient (MCC)

## System Requirements

- Python 3.x
- Scientific libraries (numpy, pandas, scikit-learn)
- 1-2 GB RAM for classification
- 4-8 CPU threads recommended

## Ancestry Codes

- 1: White/European
- 2: Black/African
- 3: Hispanic
- 4: Asian
- 6: Other

## Getting Started with the Toy Dataset

The `Toy_dataset` directory contains example data to help you understand and test the pipeline:

### Input Data Format
The toy dataset `mixed_samples.xlsx` follows the required format:
- Excel file with ancestry components as columns
- Each row represents one sample
- Values should be proportions (0-1) or percentages (0-100)
- Required columns: AFR, AMR, EAS, EUR, SAS (representing African, American, East Asian, European, and South Asian ancestry components)

### Running the Models

1. Stage 1 - Basic Prediction:
```bash
cd PredictGeoGroup_ML_model
python PredictGeoGroup1.py --input Toy_dataset/mixed_samples.xlsx
```

2. Stage 2 - Detailed Analysis:
```bash
python PredictGeoGroup2.py --input Toy_dataset/mixed_samples.xlsx
```

### Expected Output
The models will generate:
- `predictions.csv`: Contains basic predictions for each sample with continental ancestry assignments
- `detailed_analysis.csv`: Includes probability scores, confidence metrics, and detailed ancestry breakdowns
- Visualization plots in the `plots` directory:
  - ROC curves for each ancestry component
  - Precision-Recall curves
  - Confusion matrices
  - Probability heatmaps

### Configuration
Default configuration files are provided in `Toy_dataset/config`:
- `model_params.json`: ML model parameters including:
  - Feature selection thresholds
  - Model hyperparameters
  - Cross-validation settings
- `thresholds.json`: Classification thresholds for:
  - Minimum confidence scores
  - Borderline case definitions
  - Multi-ancestry detection
- `component_weights.json`: Feature importance weights for:
  - Each ancestry component
  - SNP selection criteria
  - Quality control parameters

### Example Output Interpretation
1. Basic Prediction (`predictions.csv`):
   - Sample ID
   - Predicted ancestry group
   - Confidence score
   - Top contributing components

2. Detailed Analysis (`detailed_analysis.csv`):
   - Sample ID
   - Top-1 and Top-2 ancestry predictions
   - Probability scores for each ancestry component
   - Borderline case flag
   - Quality metrics
