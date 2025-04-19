import pandas as pd
import os

def count_samples_in_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return len(df)
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return 0

def analyze_directory(directory_path):
    print(f"\nAnalyzing directory: {directory_path}")
    print("-" * 50)
    
    # Count training samples
    training_file = os.path.join(directory_path, "training_set.csv")
    if os.path.exists(training_file):
        train_samples = count_samples_in_csv(training_file)
        print(f"Training samples: {train_samples}")
    
    # Count test samples
    test_files = [
        "test_1KG_1k_with_predictions.csv",
        "test_Germline_GATK_HaplotypeCaller_1k_with_predictions.csv",
        "test_Germline_Strelka2_1k_with_predictions.csv",
        "test_RNASeq_with_predictions.csv",
        "test_Somatic_Verdict_1k_with_predictions.csv"
    ]
    
    for test_file in test_files:
        file_path = os.path.join(directory_path, test_file)
        if os.path.exists(file_path):
            test_samples = count_samples_in_csv(file_path)
            print(f"{test_file}: {test_samples} samples")

if __name__ == "__main__":
    # Directory to analyze
    directory = r"D:\AncestryGeni\PredictGeoGroup_ML_model\figD\figD_train_Germline_GATK_HaplotypeCaller_1k_lsqr"
    analyze_directory(directory) 