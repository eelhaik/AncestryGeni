import os
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import precision_score, recall_score, f1_score, matthews_corrcoef
from sklearn.metrics import cohen_kappa_score, roc_auc_score
import time
import matplotlib.pyplot as plt

def normalize_df(df, threshold=0.1):
   features = df[feature_columns].copy()
   features = features.apply(lambda x: np.where(x < threshold, 0, x))
   row_sums = features.sum(axis=1)
   features = features.div(row_sums, axis=0)
   
   if features.isna().any().any():
       return normalize_df(df, threshold - 0.01)
   return features

# Paths
model_path = "./ML_models/best_model.pkl"
filtered_test_file = "Filtered_New_Test_Samples_No_Code6.xlsx"
output_folder = "./Filtered_Test_Results" 
metrics_output_path = os.path.join(output_folder, "evaluation_metrics.txt")
os.makedirs(output_folder, exist_ok=True)

# Load model and data
model = joblib.load(model_path)
filtered_test_df = pd.read_excel(filtered_test_file)

# Define columns
feature_columns = [f'Col{i}' for i in range(1, 13)]
column_mapping = {
   'Col1': 'Z_Africa1', 'Col2': 'Z_Africa2', 
   'Col3': 'Z_CentralAsia', 'Col4': 'Z_CentralEurope',
   'Col5': 'Z_EastAsia', 'Col6': 'Z_FarEastAsia',
   'Col7': 'Z_India', 'Col8': 'Z_NativeAmerica',
   'Col9': 'Z_Scandinavia', 'Col10': 'Z_SouthEastAsia',
   'Col11': 'Z_SouthEurope', 'Col12': 'Z_UK'
}

# Find minimum sample size across noise levels
noise_level_counts = filtered_test_df.groupby('Noise_Level').size()
min_samples = noise_level_counts.min()
print(f"\nSample counts per noise level before balancing:")
print(noise_level_counts)
print(f"\nBalancing all noise levels to {min_samples} samples")

# Write header
with open(metrics_output_path, "w") as metrics_file:
   metrics_file.write("EVALUATION METRICS FOR FILTERED TEST SETS\n")
   metrics_file.write("=" * 50 + "\n")

# Collect metrics for plotting
accuracy_data = {}
f1_data = {}
auc_data = {}
mcc_data = {}
kappa_data = {}
precision_data = {}
recall_data = {}

# Process each noise level
noise_levels = filtered_test_df['Noise_Level'].unique()
for noise_level in noise_levels:
   start_time = time.time()
   
   # Filter and balance data
   test_subset = filtered_test_df[filtered_test_df['Noise_Level'] == noise_level]
   if len(test_subset) > min_samples:
       test_subset = test_subset.sample(n=min_samples, random_state=42)
   
   print(f"\nNoise Level {noise_level}: {len(test_subset)} samples")
   
   # Prepare features
   X_test = normalize_df(test_subset)
   X_test = X_test.rename(columns=column_mapping)
   y_test = test_subset['Code']
   
   # Predict
   y_pred = model.predict(X_test)
   y_pred_proba = model.predict_proba(X_test)
   
   # Calculate metrics
   conf_matrix = confusion_matrix(y_test, y_pred)
   accuracy = accuracy_score(y_test, y_pred)
   precision = precision_score(y_test, y_pred, average='weighted')
   recall = recall_score(y_test, y_pred, average='weighted')
   f1 = f1_score(y_test, y_pred, average='weighted')
   mcc = matthews_corrcoef(y_test, y_pred)
   kappa = cohen_kappa_score(y_test, y_pred)
   auc = roc_auc_score(pd.get_dummies(y_test), y_pred_proba, multi_class='ovr')
   training_time = time.time() - start_time

   # Store metrics for plotting
   accuracy_data[noise_level] = accuracy
   f1_data[noise_level] = f1
   auc_data[noise_level] = auc
   mcc_data[noise_level] = mcc
   kappa_data[noise_level] = kappa
   precision_data[noise_level] = precision
   recall_data[noise_level] = recall

   # Save predictions and write metrics [rest of the loop code remains the same]
   ...

# Plot all metrics in one figure
plt.figure(figsize=(12, 6), dpi=600)

metrics_to_plot = {
   'Accuracy': (accuracy_data, 'blue', 'o'),
   'F1 Score': (f1_data, 'red', 's'),
   'AUC': (auc_data, 'green', '^'),
   'MCC': (mcc_data, 'purple', 'd'),
   'Kappa': (kappa_data, 'orange', '*'),
   'Precision': (precision_data, 'brown', 'p'),
   'Recall': (recall_data, 'pink', 'h')
}

for metric_name, (data, color, marker) in metrics_to_plot.items():
   plt.plot(list(data.keys()), list(data.values()), 
            marker=marker, label=metric_name, linewidth=2, color=color)

plt.title('Model Performance Metrics vs Noise Level')
plt.xlabel('Noise Level')
plt.ylabel('Score')
plt.ylim(0.6, 1.0)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(output_folder, 'all_metrics_plot.png'), dpi=600, bbox_inches='tight')
plt.close()