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

# Population mapping
POPULATION_NAMES = {
    0: 'European',    # Code 1 gets converted to 0
    1: 'African',     # Code 2 gets converted to 1
    2: 'Asian',       # Code 3 gets converted to 2
    3: 'Amerindian'   # Code 4 gets converted to 3
}

def train_lda_classifier(X, y):
    lda = LinearDiscriminantAnalysis(
        solver='lsqr',
        shrinkage='auto',
        store_covariance=True,
        tol=1e-4
    )
    return lda.fit(X, y)

def validate_data(df: pd.DataFrame, expected_columns: List[str]) -> bool:
    if 'Caller' in df.columns and 'Filename' in df.columns:
        df['Dataset'] = df['Caller']
        df['Sample'] = df['Filename']
        df.drop(['Caller', 'Filename'], axis=1, inplace=True)
    
    missing_cols = [col for col in expected_columns if col not in df.columns]
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
            for pop, auc in metrics_dict.items():
                f.write(f"{pop}: {auc:.4f}\n")
        else:
            for pop, (precision, recall) in metrics_dict.items():
                f.write(f"{pop}:\n")
                f.write("Precision: " + ", ".join([f"{p:.4f}" for p in precision]) + "\n")
                f.write("Recall: " + ", ".join([f"{r:.4f}" for r in recall]) + "\n\n")

def plot_roc_pr_for_all_tests(base_output_dir: str = "plots", dpi: int = 650, colors: Optional[List[str]] = None) -> None:
    try:
        base_path = Path(base_output_dir)
        roc_path = base_path / "roc_curves"
        pr_path = base_path / "pr_curves"
        
        for path in [base_path, roc_path, pr_path]:
            path.mkdir(exist_ok=True)
        
        if colors is None:
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        # Initialize/clear metrics files
        roc_metrics_file = roc_path / "all_roc_metrics.txt"
        pr_metrics_file = pr_path / "all_pr_metrics.txt"
        for file in [roc_metrics_file, pr_metrics_file]:
            with open(file, 'w') as f:
                f.write("AUC Values\n")
                f.write("==========\n")
        
        required_columns = ["Dataset", "Sample", "SampleCode", "Code"]
        test_files = [f for f in os.listdir() if f.startswith('test_')]

        for test_file in test_files:
            try:
                test_name = test_file.replace('test_', '').replace('_with_predictions.csv', '.csv')
                train_file = f'training_pair_for_{test_name}'
                
                if not os.path.exists(train_file):
                    logger.warning(f"No matching training file found for {test_file}")
                    continue
                
                logger.info(f"Processing pair: {train_file} - {test_file}")
                
                train_data = pd.read_csv(train_file, delimiter='\t')
                validate_data(train_data, required_columns)
                
                X_train = train_data.drop(columns=required_columns)
                y_train = train_data["Code"]
                le = LabelEncoder()
                y_train = le.fit_transform(y_train)
                
                lda = train_lda_classifier(X_train, y_train)
                
                test_data = pd.read_csv(test_file, delimiter='\t')
                validate_data(test_data, required_columns)
                test_data = test_data.drop(columns=['predicted_code'], errors='ignore')

                X_test = test_data.drop(columns=required_columns)
                y_test = test_data["Code"]
                y_test = le.transform(y_test)
                
                y_proba = lda.predict_proba(X_test)
                
                for plot_type in ['roc', 'pr']:
                    fig, ax = plt.subplots(figsize=(2, 2))
                    ax.grid(True, alpha=0.2, linestyle='--')
                    metrics = {}
                    
                    for i in range(len(le.classes_)):
                        population = POPULATION_NAMES[i]
                        y_true_class = (y_test == i).astype(int)
                        y_proba_class = y_proba[:, i]
                        
                        if plot_type == 'roc':
                            fpr, tpr, _ = roc_curve(y_true_class, y_proba_class)
                            roc_auc = roc_auc_score(y_true_class, y_proba_class)
                            metrics[population] = roc_auc
                            ax.plot(fpr, tpr, color=colors[i % len(colors)])
                            
                            curves = bootstrap_curves(y_true_class, y_proba_class)
                            x_values = np.linspace(0, 1, 100)
                            bounds = calculate_curve_bounds(curves['roc_curves'], x_values)
                            
                            ax.fill_between(x_values, bounds['lower'], bounds['upper'],
                                          color=colors[i % len(colors)], alpha=0.2)
                            
                            if i == 0:
                                ax.plot([0, 1], [0, 1], 'k--')
                        else:
                            precision, recall, _ = precision_recall_curve(y_true_class, y_proba_class)
                            metrics[population] = (precision, recall)  # Store tuple of arrays
                            ax.plot(recall, precision, color=colors[i % len(colors)])
                            
                            curves = bootstrap_curves(y_true_class, y_proba_class)
                            x_values = np.linspace(0, 1, 100)
                            bounds = calculate_curve_bounds(curves['pr_curves'], x_values)
                            
                            ax.fill_between(x_values, bounds['lower'], bounds['upper'],
                                          color=colors[i % len(colors)], alpha=0.2)
                    
                    # Remove all labels and text
                    ax.set_xticks([])
                    ax.set_yticks([])
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])
                    
                    plt.tight_layout()
                    
                    # Save the plot
                    output_path = roc_path if plot_type == 'roc' else pr_path
                    output_file = output_path / f"{test_name}_{plot_type}.png"
                    plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
                    plt.close(fig)
                
                    # save_metrics_for_test(metrics, test_name, metrics_file)
                    metrics_file = roc_metrics_file if plot_type == 'roc' else pr_metrics_file
                    save_metrics_for_test(metrics, test_name, metrics_file, plot_type=plot_type)
                    
                    logger.info(f"Saved {plot_type} plot and metrics for {test_name}")
                
            except Exception as e:
                logger.error(f"Error processing pair {test_file}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    plot_roc_pr_for_all_tests()