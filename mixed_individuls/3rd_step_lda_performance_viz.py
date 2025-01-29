import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, precision_recall_curve, roc_auc_score
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import resample
from typing import List, Dict, Optional, Tuple
from tqdm import tqdm
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Updated mapping for regions
REGION_NAMES = {
    0: 'Subsaharian Africa',
    1: 'America',
    2: 'Asia',
    3: 'Europe',
    4: 'Middle East',
    5: 'North Africa',
    6: 'Oceania'
}

# Define the genetic ancestry columns
TRAINING_COLUMNS = [
    'Africa1', 'Africa2', 'CentralAsia', 'CentralEurope', 
    'EastAsia', 'FarEastAsia', 'India', 'NativeAmerica',
    'Scandinavia', 'SouthEastAsia', 'SouthEurope', 'UK'
]

def train_lda_classifier(X, y):
    lda = LinearDiscriminantAnalysis(
        solver='lsqr',
        shrinkage='auto',
        store_covariance=True,
        tol=1e-4
    )
    return lda.fit(X, y)

def validate_data(df: pd.DataFrame, required_columns: List[str]) -> bool:
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    return True

def bootstrap_curves(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    n_bootstraps: int = 1000,
    random_state: Optional[int] = 42
) -> Dict[str, List[Tuple[np.ndarray, np.ndarray]]]:
    if random_state is not None:
        np.random.seed(random_state)
    
    roc_curves = []
    pr_curves = []
    
    for _ in tqdm(range(n_bootstraps), desc="Bootstrapping", leave=False):
        indices = resample(range(len(y_true)), replace=True)
        y_true_boot = y_true[indices]
        y_proba_boot = y_proba[indices]
        
        fpr, tpr, _ = roc_curve(y_true_boot, y_proba_boot)
        roc_curves.append((fpr, tpr))
        
        precision, recall, _ = precision_recall_curve(y_true_boot, y_proba_boot)
        pr_curves.append((precision, recall))
    
    return {
        'roc_curves': roc_curves,
        'pr_curves': pr_curves
    }

def calculate_curve_bounds(curves: List[Tuple[np.ndarray, np.ndarray]], x_values: np.ndarray) -> Dict[str, np.ndarray]:
    interpolated_y = []
    for x_curve, y_curve in curves:
        y_interp = np.interp(x_values, x_curve, y_curve)
        interpolated_y.append(y_interp)
    
    interpolated_y = np.array(interpolated_y)
    return {
        'lower': np.percentile(interpolated_y, 2.5, axis=0),
        'upper': np.percentile(interpolated_y, 97.5, axis=0),
        'mean': np.mean(interpolated_y, axis=0)
    }

def save_metrics_for_test(metrics_dict: dict, test_name: str, output_file: str, plot_type: str = 'roc'):
    with open(output_file, 'a') as f:
        f.write(f"\n{test_name}:\n")
        f.write("-" * (len(test_name) + 1) + "\n")
        if plot_type == 'roc':
            for region, auc in metrics_dict.items():
                f.write(f"{region}: {auc:.4f}\n")
        else:
            for region, (precision, recall) in metrics_dict.items():
                f.write(f"{region}:\n")
                f.write("Precision: " + ", ".join([f"{p:.4f}" for p in precision]) + "\n")
                f.write("Recall: " + ", ".join([f"{r:.4f}" for r in recall]) + "\n\n")

def plot_roc_pr_for_regions(base_output_dir: str = "plots", dpi: int = 650) -> None:
    try:
        base_path = Path(base_output_dir)
        roc_path = base_path / "roc_curves"
        pr_path = base_path / "pr_curves"
        
        for path in [base_path, roc_path, pr_path]:
            path.mkdir(exist_ok=True)
        
        # Color scheme for regions
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
        
        # Initialize metrics files
        roc_metrics_file = roc_path / "all_roc_metrics.txt"
        pr_metrics_file = pr_path / "all_pr_metrics.txt"
        for file in [roc_metrics_file, pr_metrics_file]:
            with open(file, 'w') as f:
                f.write("AUC Values\n")
                f.write("==========\n")

        # Load and process the data
        try:
            # Load training and testing data
            train_data = pd.read_excel("training_set.xlsx")
            test_data = pd.read_excel("testing_set.xlsx")
            
            # Convert comma decimals to periods if needed
            for col in TRAINING_COLUMNS:
                if train_data[col].dtype == object:
                    train_data[col] = train_data[col].str.replace(',', '.').astype(float)
                if test_data[col].dtype == object:
                    test_data[col] = test_data[col].str.replace(',', '.').astype(float)
            
            # Prepare features and labels
            X_train = train_data[TRAINING_COLUMNS]
            X_test = test_data[TRAINING_COLUMNS]
            
            le = LabelEncoder()
            y_train = le.fit_transform(train_data['Region'])
            y_test = le.transform(test_data['Region'])
            
            # Train model and get predictions
            lda = train_lda_classifier(X_train, y_train)
            y_proba = lda.predict_proba(X_test)
            
            # Generate plots for each class
            for plot_type in ['roc', 'pr']:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.grid(True, alpha=0.2, linestyle='--')
                metrics = {}
                legend_lines = []
                legend_labels = []
                
                for i in range(len(le.classes_)):
                    region = REGION_NAMES[i]
                    y_true_class = (y_test == i).astype(int)
                    y_proba_class = y_proba[:, i]
                    
                    if plot_type == 'roc':
                        fpr, tpr, _ = roc_curve(y_true_class, y_proba_class)
                        roc_auc = roc_auc_score(y_true_class, y_proba_class)
                        metrics[region] = roc_auc
                        line, = ax.plot(fpr, tpr, color=colors[i])
                        legend_lines.append(line)
                        legend_labels.append(f'{region} (AUC = {roc_auc:.2f})')
                        
                        curves = bootstrap_curves(y_true_class, y_proba_class)
                        x_values = np.linspace(0, 1, 100)
                        bounds = calculate_curve_bounds(curves['roc_curves'], x_values)
                        
                        ax.fill_between(x_values, bounds['lower'], bounds['upper'],
                                      color=colors[i], alpha=0.2)
                        
                        if i == 0:
                            ax.plot([0, 1], [0, 1], 'k--', label='Random')
                    else:
                        precision, recall, _ = precision_recall_curve(y_true_class, y_proba_class)
                        metrics[region] = (precision, recall)
                        line, = ax.plot(recall, precision, color=colors[i])
                        legend_lines.append(line)
                        legend_labels.append(region)
                        
                        curves = bootstrap_curves(y_true_class, y_proba_class)
                        x_values = np.linspace(0, 1, 100)
                        bounds = calculate_curve_bounds(curves['pr_curves'], x_values)
                        
                        ax.fill_between(x_values, bounds['lower'], bounds['upper'],
                                      color=colors[i], alpha=0.2)
                
                # Add labels and legend
                ax.set_xlabel('False Positive Rate' if plot_type == 'roc' else 'Recall')
                ax.set_ylabel('True Positive Rate' if plot_type == 'roc' else 'Precision')
                ax.set_title('ROC Curves' if plot_type == 'roc' else 'Precision-Recall Curves')
                
                legend = ax.legend(legend_lines, legend_labels, 
                                 bbox_to_anchor=(1.05, 1), 
                                 loc='upper left')
                
                plt.tight_layout()
                
                # Save plots
                output_path = roc_path if plot_type == 'roc' else pr_path
                output_file = output_path / f"region_prediction_{plot_type}.png"
                plt.savefig(output_file, dpi=dpi, bbox_inches='tight',
                          bbox_extra_artists=(legend,))
                plt.close(fig)
                
                # Save metrics
                metrics_file = roc_metrics_file if plot_type == 'roc' else pr_metrics_file
                save_metrics_for_test(metrics, "Region_Prediction", metrics_file, plot_type=plot_type)
                
                logger.info(f"Saved {plot_type} plot and metrics")
                
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
                
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    plot_roc_pr_for_regions()