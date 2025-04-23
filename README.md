# AncestryGeni Pipeline

AncestryGeni is a novel ancestry pipeline for small and noisy sequence data that identifies continental populations from genomic data. The pipeline supports human genome builds GRCh37 and GRCh38 and is compatible with a variety of sequencing data types, including whole-genome sequencing (WGS), whole-exome sequencing (WES), and RNA-Seq.

## Pipeline Overview

The pipeline operates in two main stages:

1. **First Stage (ADMIXTURE)**: Defines global gene pools using unsupervised ADMIXTURE on reference individuals, followed by supervised ADMIXTURE to estimate ancestry proportions of test samples.
2. **Second Stage (Machine Learning)**: Applies a supervised machine learning model to predict continental affiliations based on inferred ancestry proportions.

## Quick Start

```bash
git clone https://github.com/eelhaik/AncestryGeni.git
cd AncestryGeni
```

## Directory Structure

```
AncestryGeni/
├── 1_ADMIXTURE Stage/
│   ├── Admixture/
│   │   └── admixture32
│   ├── Input data/
│   │   └── ReferencePops.zip
│   └── pipeline setup/
│       ├── Admixture.sh
│       ├── AnalyzeFiles.sh
│       ├── Get1Kg.sh
│       ├── Parameters.txt
│       ├── Run_AncestryGeni.txt
│       ├── Summarize_results_one_row.sh
│       └── Summarize_results_two_row.sh
└── 2_MACHINE Learning Stage/
    ├── Comparing Different Classifications/
    │   └── comparing_models.ipynb
    ├── Example Output/
    │   └── figA/
    ├── Input data/
    │   ├── Parameters.txt
    │   ├── RNASeq.txt
    │   └── RNASeq_1kg/
    ├── Noise analysis/
    │   ├── admix_3rd_Step_for_noise_analysis_and_plot.py
    │   ├── filtering_1st_Step_for_noise_analysis.py
    │   └── run_tests_with_filtered_samples_2nd_Step_for_noise_analysis.py
    ├── Predict GeoGroup/
    │   ├── AnalyzeVEPFile.py
    │   ├── FilterPFile.py
    │   ├── PredictGeoGroup1.py
    │   ├── PredictGeoGroup2.py
    │   ├── README.md
    │   ├── config.json
    │   ├── count_samples.py
    │   ├── mixed_samples.xlsx
    │   ├── module_model_executor.py
    │   └── module_preprocessor.py
    ├── Toy dataset for ML/
    │   └── mixed_samples.xlsx
    └── Tuning and Visualization/
        ├── lda_performance_viz.py
        └── tune_lda_parameters.py
```

## First Stage: ADMIXTURE

### 1.1 Rationale
The training process involves two main parts:
1. Unsupervised ADMIXTURE is applied to a subset of reference individuals from the 1000 Genomes Project to identify 12 global gene pools (ancestry components).
2. Supervised ADMIXTURE estimates the ancestry proportions of each test sample based on these predefined components.

### 1.2 Files Needed
Reference Population Data – `ReferencePops.zip` in the `1_ADMIXTURE Stage/Input data/` directory includes:
- VCF files (Variant Call Format)
- PLINK files (.bed, .bim, .fam)
- Population metadata files
- Geographic coordinates

### 1.3 VCF to PLINK Conversion
To convert a VCF file to PLINK format:
```bash
plink --vcf input.vcf --make-bed --out output_prefix
```

### 1.4 Configuration Files

#### Parameters.txt
Located in `1_ADMIXTURE Stage/pipeline setup/`:
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

#### config.json
Located in `2_MACHINE Learning Stage/Predict GeoGroup/`:
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

### 1.5 Commands
To set up and run the pipeline:
```bash
cd 1_ADMIXTURE Stage/pipeline setup
bash Run_AncestryGeni.txt
```

## Second Stage: Machine Learning Classification

### 2.1 Basic Classification – PredictGeoGroup1.py
```bash
cd ../2_MACHINE Learning Stage/Predict GeoGroup
python PredictGeoGroup1.py
```
Performs initial ancestry classification using broad continental groups. This stage provides:
- Quick and efficient initial assessment
- Broad ancestry categories (European, African, Asian, etc.)
- Confusion matrix for performance evaluation
- Direct ancestry assignments

### 2.2 Detailed Classification – PredictGeoGroup2.py
```bash
python PredictGeoGroup2.py
```
Performs detailed prediction with:
- Probability scores for each ancestry
- Alternative ancestry possibilities
- Analysis of admixed populations
- Extensive visualizations
- Detailed reports

### 2.3 Visualization Tools
```bash
cd ../Tuning and Visualization
python lda_performance_viz.py --input ../results/predictions.csv --output ./visualizations/
```
Provides ROC and PR curve visualizations.

### 2.4 Usage Flow
Recommended order of operations:
1. Run `PredictGeoGroup1.py` for initial ancestry classification
2. Run `PredictGeoGroup2.py` for deeper analysis
3. Visualize results using `lda_performance_viz.py`

## Example Usage with Toy Dataset

The toy dataset is located in `2_MACHINE Learning Stage/Toy dataset for ML/`:
- `mixed_samples.xlsx`: Sample genetic data with known ancestry components
- Example configuration files
- Expected output examples

### Sample Data Format
```
Sample_Name    Original_HGDP_IDs    True_Ancestry    Predicted_Ancestry    Top1_Prediction    Top1_Probability    Top2_Prediction    Top2_Probability
HGDP00336      HGDP00336            Europe-Europe    Europe-Europe         Europe-Europe      0.554318            Africa-Europe      0.445644
```

Important Notes:
1. All ancestry proportions must be decimal numbers between 0 and 1
2. Values use commas as decimal separators (European format)
3. The sum of ancestry components must equal 1.0
4. Sample_Name and Final_HGDP are identifiers
5. Ancestry_Label indicates the known ancestry group

## Output Files

### First Stage Outputs
- `*.Q`: Ancestry proportions
- `*.P`: Allele frequencies
- `*.log`: Convergence and runtime info

### Second Stage Outputs
- `_with_predictions.csv`: Predicted ancestry
- `output_basic.txt` / `output_detailed.txt`: Metrics
- `best_model.pkl`: Saved model
- Visualizations: Confusion matrix, heatmaps

## Performance Metrics
- Accuracy
- F1-score
- Precision/Recall
- Cohen's kappa
- MCC

## System Requirements
- Python 3.x (with numpy, pandas, scikit-learn, joblib, commentjson)
- ADMIXTURE software
- 1–2 GB RAM for classification
- 4–8 CPU threads recommended
- 8 GB RAM for ADMIXTURE

## Reference Population Files
Located in `1_ADMIXTURE Stage/Input data/ReferencePops.zip`:
- For GRC38:
  - `Admixture_reference_pops.chr_pos`
  - `Admixture_reference_pops`
  - `SNPs.txt`
  - `Admixture_reference_pops_no_rs.bim`

## Citation

**AncestryGeni: A novel genetic ancestry pipeline for small and noisy sequence data**  
_Eran Elhaik, Sara Behnamian, Michael Howe, Hongwei Tang, Huihuang Yan, Shulan Tian,  
Suganti Shivaram, Cinthya Zepeda Mendoza, Kylee MacLachlan, Saad Usmani,  
Mehdi Pirooznia, Gareth Morgan, Patrick Blaney, Francesco Maura, Linda B. Baughn_

---
