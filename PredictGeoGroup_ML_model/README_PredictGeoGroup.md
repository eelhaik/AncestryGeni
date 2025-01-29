# PredictGeoGroup

## Overview
PredictGeoGroup is a machine learning-based tool designed to predict geographic ancestry groups based on genetic data. The main script, `PredictGeoGroup.py`, orchestrates the pipeline, utilizing multiple supporting modules for preprocessing, model execution, evaluation, and visualization.

## Repository Structure
```
PredictGeoGroup/
│-- AnalyzeVEPFile.py                 # Script for analyzing variant effect prediction (VEP) files
│-- comparing_models.ipynb             # Jupyter notebook for comparing different models
│-- config.json                        # Main configuration file
│-- config_CP.json                      # Configuration for CP-specific settings
│-- config_Modern.json                  # Configuration for modern datasets
│-- FilterPFile.py                      # Script for filtering P files
│-- lda_performance_viz.py              # Script for visualizing LDA performance
│-- module_model_executor.py            # Module for executing machine learning models
│-- module_preprocessor.py              # Module for data preprocessing
│-- PredictContinentalPopulations.py    # Predicts continental-level ancestry groups
│-- PredictGeoGroup.py                  # **Main script for geographic ancestry prediction**
│-- tune_lda_parameters.py              # Script for tuning hyperparameters of LDA models
```

## Main Script: `PredictGeoGroup.py`
- The core script of the project.
- Loads genetic data and configurations from `config.json`.
- Preprocesses data using `module_preprocessor.py`.
- Executes machine learning models using `module_model_executor.py`.
- Evaluates model performance using various metrics.
- Saves results and predictions for further analysis.

## Supporting Modules
- **`module_preprocessor.py`**: Handles data preprocessing, feature engineering, and normalization.
- **`module_model_executor.py`**: Manages machine learning model training, evaluation, and execution.
- **`FilterPFile.py`**: Filters and processes genetic data files.
- **`AnalyzeVEPFile.py`**: Analyzes variant effect prediction (VEP) results.
- **`PredictContinentalPopulations.py`**: Runs a high-level prediction of ancestry at the continental level.
- **`lda_performance_viz.py`**: Visualizes performance metrics of LDA models.

## Model Comparison & Tuning
- **`comparing_models.ipynb`**: Jupyter notebook for comparing different ML models to identify the best-performing one.
- **`tune_lda_parameters.py`**: Fine-tunes hyperparameters for LDA models to optimize performance.

## Configuration Files
- **`config.json`**: Main configuration file specifying paths, data sources, and parameters.
- **`config_CP.json` & `config_Modern.json`**: Alternative configurations for different datasets.

## Output & Results
- **Model files**: Saved in `./ML_models/best_model.pkl`.
- **Evaluation metrics**: Stored in `best_performance_metrics.xlsx`.
- **Results and visualizations**: Saved in `./ML_results/`.

## Usage
1. Ensure the required dependencies are installed.
2. Modify `config.json` to specify data sources and parameters.
3. Run `PredictGeoGroup.py`:
   ```sh
   python PredictGeoGroup.py
   ```
4. Analyze results in `./ML_results/`.
5. Use `comparing_models.ipynb` to assess model performance.
6. Tune hyperparameters using `tune_lda_parameters.py` if needed.

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
