# Ancestry Pipeline README

This pipeline is designed for human genome builds GRC37 and GRC38.

## 1. Setting Up the Parameters File

### File: `Parameters.txt`
- **Do Not Rename**: The pipeline scripts are hardcoded to read from `Parameters.txt`.

### Parameters Overview

- **ADMIXTURE_DIR**: Directory where the ADMIXTURE tool is installed.
- **INPUT_DIR**: Directory containing raw VCF files of the samples.

### Output Folders
These folders need to be created manually as they are used by various scripts in the pipeline:
- **OUTPUT_DIR**: Main output directory.
- **OUTPUT_DIR_1KG**: Output directory for 1KG data.
- **OUTPUT_DIR_FINAL**: Final output directory.
- **OUTPUT_ADMIXTURE_DIR**: Directory where you will run the pipeline.

### Output Files
- **OUTPUT_FILE_TABLE**: Main output file containing ancestry counts.
- **OUTPUT_FILE**: File listing the number of SNPs analyzed per sample (useful for quality control).

### Reference Population Files (GRC38 Folder)
- **REF_CHR_POS**: `ReferencePops/GRC38/Admixture_reference_pops.chr_pos`
- **ADMIXTURE_REFERENCE_POPS**: `ReferencePops/GRC38/Admixture_reference_pops`
- **REF_SNPS**: `ReferencePops/GRC38/SNPs.txt`
- **BIM_NO_RS**: `ReferencePops/GRC38/Admixture_reference_pops_no_rs.bim`

### Additional Parameters
- **DB_NAME**: Name of the dataset being analyzed; used in `OUTPUT_FILE_TABLE` to differentiate results.
- **NUM_OF_LINES**: Number of lines per sample in the files (e.g., 1 for `Germline_GATK_HaplotypeCaller`, 2 for `Somatic_Verdict`).

## 2. Installing ADMIXTURE

### Installation Instructions
- Install ADMIXTURE from the provided zip file located in the `Admixture` folder.

## 3. Setting Up the `OUTPUT_ADMIXTURE_DIR`

- Use this directory to execute all pipeline commands.
- This directory should contain pipeline files, associated files, and the liftover tool.

## 4. Running the Pipeline

### Command
./Run_AncestryGeni.txt

### Output
- The pipeline will run four scripts and clean up temporary files.
- All output folders will be populated.
- Two output files will be generated (e.g., `RNASeq.txt`, `RNASeq_counts.txt`).

## Directory Structure
- **PredictGeoGroup_ML_model/**: Contains the machine learning models and scripts for geographic prediction
  - `README_PredictGeoGroup.md`: Detailed documentation for the ML model components, including:
    - Two-stage prediction pipeline (PredictGeoGroup1.py and PredictGeoGroup2.py)
    - Model tuning and visualization tools
    - Configuration options and dependencies
  - `tuning_and_vis/`: Contains scripts for model tuning and visualization
  - Main prediction scripts: `PredictGeoGroup1.py` and `PredictGeoGroup2.py`
  - Configuration files: `config.json`, `config_CP.json`, `config_Modern.json`

## 5. Continental Population Prediction - Stage 1 (PredictGeoGroup1)

The first stage uses PredictGeoGroup1.py to assign individuals to continental ancestry groups. This stage provides the initial ancestry estimation that forms the basis for more detailed analysis. It also generates a confusion matrix to evaluate the model's performance.

## 6. Continental Population Prediction - Stage 2 (PredictGeoGroup2)

This stage provides more detailed interpretation, particularly for highly admixed individuals and model confidence. It reports top-1 and top-2 classification probabilities for each individual, helping to identify borderline cases and provide more nuanced ancestry predictions.

### Configuration
Users configure a separate JSON file (config.json) specifying:
- Training and testing data files
- Ancestry component columns
- Classification parameters

### Analysis Features
- Sample filtering and normalization
- Stratified splitting
- Supervised model training and prediction
- Support for both broad and fine-scale ancestry input
- Detailed Excel reports and visualizations
- Confusion matrices and probability heatmaps

### Output Files
- Individual-level predictions (*_with_predictions.csv)
- Performance summaries (output_basic.txt, output_detailed.txt)
- Trained model files (best_model.pkl)

### Performance Metrics
- Accuracy
- F1-score
- Precision
- Recall
- Cohen's kappa
- Matthews correlation coefficient (MCC)
- Confusion matrices

### System Requirements
- Python 3
- Standard scientific libraries (numpy, pandas, scikit-learn, joblib, commentjson)
- 1-2 GB RAM for supervised classification
- 4-8 CPU threads recommended for ADMIXTURE analysis (up to 8 GB RAM)

## 7. Example Files
Example files are shown in the `Example` folder.
**Note:** All genetic data was deleted for privacy reasons.

## 8. Handling Different Human Builds

- **For GRC37 Files**: The pipeline will perform a liftover to GRC38.
- **For GRC38 Files**: No liftover is required.

## Citation

If you use this code, please cite the following paper:

**AncestryGeni: A novel genetic ancestry pipeline for small and noisy sequence data**  
*Eran Elhaik, Sara Behnamian, Michael Howe, Hongwei Tang, Huihuang Yan, Shulan Tian,  
Suganti Shivaram, Cinthya Zepeda Mendoza, Kylee MacLachlan, Saad Usmani,  
Mehdi Pirooznia, Gareth Morgan, Patrick Blaney, Francesco Maura, Linda B. Baughn*  

**Preprint/Paper Link:** [I will update this part later]  

---
