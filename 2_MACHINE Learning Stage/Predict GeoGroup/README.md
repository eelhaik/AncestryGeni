# PredictGeoGroup ML Model Documentation

## Overview
PredictGeoGroup is a machine learning tool for predicting geographic ancestry groups from genetic data. It uses two main scripts: `PredictGeoGroup1.py` for continental ancestry prediction and `PredictGeoGroup2.py` for 2-way continental prediction.

## Repository Structure
```
PredictGeoGroup/
├── AnalyzeVEPFile.py                 # VEP file analysis
├── comparing_models.ipynb            # Model comparison
├── config.json                       # Main config
├── config_CP.json                    # CP settings
├── config_Modern.json                # Modern datasets
├── FilterPFile.py                    # P file filtering
├── module_model_executor.py          # ML model execution
├── module_preprocessor.py            # Data preprocessing
├── PredictGeoGroup1.py               # Continental prediction
├── PredictGeoGroup2.py               # 2-way continental prediction
├── Toy_dataset/                      # Example data
│   ├── mixed_samples.xlsx           # Sample data
│   └── config/                      # Config files
└── tuning_and_vis/                   # Visualization tools
    ├── lda_performance_viz.py        # LDA visualization
    └── tune_lda_parameters.py        # Parameter tuning
```

## Main Scripts

### PredictGeoGroup1.py
- First step
- Assigns continental ancestry groups
- Generates confusion matrix

### PredictGeoGroup2.py
- Second step
- Performs 2-way continental prediction
- Reports classification probabilities
- Identifies borderline cases

## Supporting Modules
- **`module_preprocessor.py`**: Data preprocessing and normalization
- **`module_model_executor.py`**: Model training and evaluation
- **`FilterPFile.py`**: Genetic data file processing
- **`AnalyzeVEPFile.py`**: VEP result analysis
- **`lda_performance_viz.py`**: LDA model visualization
