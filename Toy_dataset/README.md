# AncestryGeni Toy Dataset

This directory contains example data and configuration files to demonstrate the AncestryGeni pipeline. The dataset includes a small set of samples with known ancestry components that can be used to test and understand the pipeline's functionality.

## Files Included

1. `mixed_samples.xlsx` - Example dataset containing:
   - Sample genetic components (Ancient and Modern)
   - Geographic coordinates
   - Ancestry labels
   - Sample metadata

2. `config.json` - Configuration file for the ML model with:
   - Training and testing data paths
   - Feature specifications
   - Model parameters

3. `Parameters.txt` - Pipeline configuration with:
   - Directory paths
   - Reference population settings
   - Output specifications

## Quick Start Guide

1. **Setup Environment**
   ```bash
   git clone https://github.com/eelhaik/AncestryGeni.git
   cd AncestryGeni
   ```

2. **Run the Pipeline**
   ```bash
   cd pipeline_setup
   bash Run_AncestryGeni.txt
   ```

3. **Run ML Model**
   ```bash
   cd ../PredictGeoGroup_ML_model
   python PredictGeoGroup1.py
   python PredictGeoGroup2.py
   ```

## Expected Outputs

The pipeline will generate:
- Ancestry proportion estimates
- Geographic predictions
- Performance metrics
- Visualization plots