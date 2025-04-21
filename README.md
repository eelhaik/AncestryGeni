# AncestryGeni Pipeline

AncestryGeni is a novel ancestry pipeline for small and noisy sequence data that identifies continental populations from genomic data. The pipeline supports human genome builds GRCh37 and GRCh38.

## Quick Start

```bash
git clone https://github.com/eelhaik/AncestryGeni.git
cd AncestryGeni
```

## Example Usage with Toy Dataset

We provide a toy dataset to help you get started and test the pipeline:

```bash
# Navigate to the ML model directory
cd PredictGeoGroup_ML_model

# Run Stage 1: Continental ancestry prediction 
python PredictGeoGroup1.py --input Toy_dataset/mixed_samples.xlsx

# Run Stage 2: 2-way continental ancestry prediction with probabilities
python PredictGeoGroup2.py --input Toy_dataset/mixed_samples.xlsx
```

The toy dataset includes:
- `mixed_samples.xlsx`: Sample genetic data with known ancestry components
- Example configuration files
- Expected output examples

This will generate:
- Basic ancestry predictions
- Detailed probability analysis
- Visualization plots
- Performance metrics

## Configuration Files

### 1. Parameters.txt
Main pipeline configuration file:

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

#### Key Parameters:
- **Software & Input**
  - `ADMIXTURE_DIR`: ADMIXTURE installation directory
  - `INPUT_DIR`: Directory with VCF files

- **Output Directories** (create these before running)
  - `OUTPUT_DIR`: Main results
  - `OUTPUT_DIR_1KG`: 1000 Genomes results
  - `OUTPUT_DIR_FINAL`: Final output
  - `OUTPUT_ADMIXTURE_DIR`: ADMIXTURE analysis

- **Output Files**
  - `OUTPUT_FILE_TABLE`: Ancestry counts
  - `OUTPUT_FILE`: SNP analysis QC
  - `DB_NAME`: Dataset identifier
  - `NUM_OF_LINES`: Sample line count

### 2. config.json
ML model configuration:

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

#### Key Settings:
- **Data Paths**
  - Training/testing directories and files
  - Support for multiple test files

- **Processing Options**
  - `MMRF_DATA`: Special handling for MMRF data
  - `SPLIT_DATA`: Data splitting control
  - `N_SPLITS`: Cross-validation splits

## Running the Pipeline

1. **Setup Parameters**
   - Configure `Parameters.txt`
   - Configure `config.json`
   - Create output directories

2. **Run Pipeline**
```bash
cd pipeline_setup
bash Run_AncestryGeni.txt
```

3. **Run ML Model**
```bash
cd ../PredictGeoGroup_ML_model
python PredictGeoGroup1.py  # Basic ancestry
python PredictGeoGroup2.py  # Detailed analysis
```

## Output Files

- **Ancestry Results**
  - `*_counts.txt`: Ancestry proportions
  - `*.txt`: SNP coverage metrics

- **ML Analysis**
  - Predictions: `*_with_predictions.csv`
  - Performance: `output_basic.txt`, `output_detailed.txt`
  - Models: `best_model.pkl`
  - Visualizations: Matrices and heatmaps

## System Requirements

- Python 3.x
- Scientific libraries (numpy, pandas, scikit-learn)
- 1-2 GB RAM for ML
- 4-8 CPU threads for ADMIXTURE

## Reference Population Files

For GRC38:
- `ReferencePops/GRC38/Admixture_reference_pops.chr_pos`
- `ReferencePops/GRC38/Admixture_reference_pops`
- `ReferencePops/GRC38/SNPs.txt`
- `ReferencePops/GRC38/Admixture_reference_pops_no_rs.bim`

## Citation

**AncestryGeni: A novel genetic ancestry pipeline for small and noisy sequence data**  
_Eran Elhaik, Sara Behnamian, Michael Howe, Hongwei Tang, Huihuang Yan, Shulan Tian,  
Suganti Shivaram, Cinthya Zepeda Mendoza, Kylee MacLachlan, Saad Usmani,  
Mehdi Pirooznia, Gareth Morgan, Patrick Blaney, Francesco Maura, Linda B. Baughn_

---
