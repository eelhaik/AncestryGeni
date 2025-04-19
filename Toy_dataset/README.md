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

## Notes

- This is a simplified dataset for demonstration purposes
- Real-world datasets may require additional preprocessing
- The configuration files may need adjustment for different datasets

## Troubleshooting

If you encounter NaN values in the predictions:
1. Check the input data for missing values
2. Verify the configuration files are correctly set up
3. Ensure all required dependencies are installed

## Citation

If you use this code, please cite:
**AncestryGeni: A novel genetic ancestry pipeline for small and noisy sequence data**
_Eran Elhaik, Sara Behnamian, Michael Howe, Hongwei Tang, Huihuang Yan, Shulan Tian,  
Suganti Shivaram, Cinthya Zepeda Mendoza, Kylee MacLachlan, Saad Usmani,  
Mehdi Pirooznia, Gareth Morgan, Patrick Blaney, Francesco Maura, Linda B. Baughn_ 