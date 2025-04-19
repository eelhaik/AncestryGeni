# Parameters File Documentation

This document explains the parameters in `Parameters.txt` used by AncestryGeni pipeline.

## Directory Settings

- `ADMIXTURE_DIR`: Path to ADMIXTURE software installation
  - Required for ancestry component estimation
  - Must contain ADMIXTURE executable

- `INPUT_DIR`: Directory containing raw VCF files
  - Input genomic data in VCF format
  - Supports GRCh37 and GRCh38 builds

## Output Directories

The following directories must be created before running the pipeline:

- `OUTPUT_DIR`: Main output directory for results
- `OUTPUT_DIR_1KG`: Directory for 1000 Genomes data output
- `OUTPUT_DIR_FINAL`: Final results directory
- `OUTPUT_ADMIXTURE_DIR`: Directory for running ADMIXTURE analysis

## Output Files

- `OUTPUT_FILE_TABLE`: Main output file containing ancestry counts
  - Format: Tab-delimited text file
  - Contains ancestry proportions for each sample

- `OUTPUT_FILE`: Quality control file
  - Lists number of SNPs analyzed per sample
  - Used for assessing data quality

## Reference Population Files

For GRC38 build:
- `REF_CHR_POS`: Chromosome positions file
  - Path: ReferencePops/GRC38/Admixture_reference_pops.chr_pos
  
- `ADMIXTURE_REFERENCE_POPS`: Reference populations file
  - Path: ReferencePops/GRC38/Admixture_reference_pops
  
- `REF_SNPS`: SNPs reference file
  - Path: ReferencePops/GRC38/SNPs.txt
  
- `BIM_NO_RS`: PLINK format reference file
  - Path: ReferencePops/GRC38/Admixture_reference_pops_no_rs.bim

## Additional Parameters

- `DB_NAME`: Dataset name for output file labeling
- `NUM_OF_LINES`: Lines per sample in input files
  - 1: For Germline_GATK_HaplotypeCaller
  - 2: For Somatic_Verdict

## Example Parameters.txt

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