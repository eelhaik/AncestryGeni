import pandas as pd

# Step 1: Load the noisy dataset from the text file
noisy_data = pd.read_csv("MMRF_478RNAseq.spikein.out.txt", sep="\t", header=None)

# Assign column names for clarity
noisy_data.columns = [
    "File", "Sample", "Noise_Level", "Col1", "Col2", "Col3", "Col4", "Col5",
    "Col6", "Col7", "Col8", "Col9", "Col10", "Col11", "Col12"
]

# Step 2: Load the RNASeq annotations from the Excel file
rnaseq_data = pd.read_excel("Datasets.xlsx", sheet_name="RNASeq")

# Merge the noisy dataset with the RNASeq data based on the 'Sample' column
merged_data = noisy_data.merge(rnaseq_data[['Sample', 'Code']], on='Sample', how='left')

# Save the merged dataset to an Excel file
merged_data.to_excel("Merged_Noise_Annotation.xlsx", index=False)
print("Merged dataset saved as 'Merged_Noise_Annotation.xlsx'")

# Step 3: Load the training set
training_data = pd.read_csv("training_pair_for_RNASeq.csv", delimiter='\t')

# Step 4: Filter samples not in the training set
# Compare based on the 'Sample' column
filtered_samples = merged_data[~merged_data['Sample'].isin(training_data['Sample'])]

# Exclude rows where 'Code' is 6
filtered_samples_no_code_6 = filtered_samples[filtered_samples['Code'] != 6]

# Count overlaps and filtered samples (for reference)
overlap_count = merged_data[merged_data['Sample'].isin(training_data['Sample'])].shape[0]
filtered_count = filtered_samples_no_code_6.shape[0]
print(f"Overlap count: {overlap_count}, Filtered count (excluding Code=6): {filtered_count}")

# Step 5: Save the filtered samples to an Excel file
filtered_samples_no_code_6.to_excel("Filtered_New_Test_Samples_No_Code6.xlsx", index=False)
print("Filtered new test samples excluding Code=6 saved as 'Filtered_New_Test_Samples_No_Code6.xlsx'")
