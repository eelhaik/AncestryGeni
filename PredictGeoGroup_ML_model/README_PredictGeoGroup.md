# PredictGeoGroup

## Overview
PredictGeoGroup is a machine learning-based tool designed to predict geographic ancestry groups based on genetic data. The pipeline includes two main scripts: `PredictGeoGroup1.py` for initial continental ancestry prediction and `PredictGeoGroup2.py` for detailed geographic prediction with probability analysis.

## Repository Structure
```
PredictGeoGroup/
│-- AnalyzeVEPFile.py                 # Script for analyzing variant effect prediction (VEP) files
│-- comparing_models.ipynb             # Jupyter notebook for comparing different models
│-- config.json                        # Main configuration file
│-- config_CP.json                     # Configuration for CP-specific settings
│-- config_Modern.json                 # Configuration for modern datasets
│-- FilterPFile.py                     # Script for filtering P files
│-- module_model_executor.py           # Module for executing machine learning models
│-- module_preprocessor.py             # Module for data preprocessing
│-- PredictGeoGroup1.py                # First stage: Continental ancestry prediction
│-- PredictGeoGroup2.py                # Second stage: Detailed geographic prediction
│-- tuning_and_vis/                    # Directory containing visualization and tuning scripts
    │-- lda_performance_viz.py         # Script for visualizing LDA performance
    │-- tune_lda_parameters.py         # Script for tuning hyperparameters of LDA models
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
   ```sh
   python PredictGeoGroup1.py
   ```
4. Run `PredictGeoGroup2.py` for detailed geographic prediction:
   ```sh
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
