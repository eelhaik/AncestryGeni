import sys
import logging
import commentjson as json
import os
import numpy as np
import pandas as pd
import joblib
import warnings
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold
from sklearn.metrics import (make_scorer, accuracy_score, f1_score, precision_score, 
                           recall_score, balanced_accuracy_score, matthews_corrcoef)
from typing import Dict, Any, Tuple, Optional
import time

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Configuration File
with open('config.json', 'r') as f:
    config = json.load(f)

# Constants
INPUT_TRAINING_FOLDER = config['INPUT_TRAINING_FOLDER']
INPUT_TRAINING_FILE = config['INPUT_TRAINING_FILE']
Training_filename = INPUT_TRAINING_FOLDER + '\\' + INPUT_TRAINING_FILE
MODELS_FOLDER = "./ML_models"
pkl_filename = 'best_model.pkl'

TRAINING_COLUMNS_FULL = ['Z_Africa1', 'Z_Africa2', 'Z_CentralAsia', 'Z_CentralEurope', 
                        'Z_EastAsia', 'Z_FarEastAsia', 'Z_India', 'Z_NativeAmerica', 
                        'Z_Scandinavia', 'Z_SouthEastAsia', 'Z_SouthEurope', 'Z_UK']
TRAINING_COLUMNS = TRAINING_COLUMNS_FULL
TARGET_COLUMN = ['Code']
COLS = config['COLS']
MMRF_DATA = config['MMRF_DATA']
norm_threshold = 0.1

def normalize_df(df: pd.DataFrame, threshold: float, Training_dataset_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the DataFrame values and handle NaN cases
    """
    df_copy = df.copy()
    
    # Map values below threshold to 0
    df_copy[TRAINING_COLUMNS] = df_copy[TRAINING_COLUMNS].map(
        lambda x: 0 if (isinstance(x, str) or x < threshold) else x
    )
    
    # Normalize rows
    row_sums = df_copy[TRAINING_COLUMNS].sum(axis=1)
    df_copy[TRAINING_COLUMNS] = df_copy[TRAINING_COLUMNS].div(row_sums, axis=0)
    
    # Check for NaN values
    has_nan = df_copy[TRAINING_COLUMNS].isna().any().any()
    
    if has_nan:
        logger.info(f"NaN values found, reducing threshold from {threshold} to {threshold - 0.01}")
        return normalize_df(Training_dataset_df.copy(), threshold - 0.01, Training_dataset_df)
        
    logger.info("Normalization completed successfully")
    return df_copy

def prepare_lda_data(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Prepare feature matrix and target vector for LDA
    """
    try:
        features = df[TRAINING_COLUMNS]
        target = df[COLS['TARGET']]
        return features, target
    except KeyError as e:
        logger.error(f"Error preparing data: {e}")
        return None, None

def create_parameter_grid() -> list:
    """
    Create optimized parameter grid for LDA tuning with compatible combinations
    """
    # Grid for lsqr and eigen solvers (with shrinkage)
    shrinkage_grid = {
        'solver': ['lsqr', 'eigen'],
        'shrinkage': ['auto'] + [round(x, 2) for x in np.arange(0.1, 0.9, 0.2)],
        'store_covariance': [True],
        'tol': [1e-4, 1e-3, 1e-2],
    }
    
    # Grid for svd solver (no shrinkage)
    svd_grid = {
        'solver': ['svd'],
        'shrinkage': [None],
        'store_covariance': [True],
        'tol': [1e-4, 1e-3, 1e-2],
    }
    
    return [shrinkage_grid, svd_grid]

def create_scoring_metrics() -> Dict[str, Any]:
    """
    Create comprehensive scoring metrics for model evaluation
    """
    scoring = {
        'accuracy': make_scorer(accuracy_score),
        'balanced_accuracy': make_scorer(balanced_accuracy_score),
        'precision_weighted': make_scorer(precision_score, average='weighted'),
        'recall_weighted': make_scorer(recall_score, average='weighted'),
        'f1_weighted': make_scorer(f1_score, average='weighted'),
        'mcc': make_scorer(matthews_corrcoef)
    }
    return scoring

def check_model_stability(grid_search: GridSearchCV, X: pd.DataFrame, y: pd.Series):
    """
    Check stability of the best model and log potential issues
    """
    results_df = pd.DataFrame(grid_search.cv_results_)
    
    # Get CV scores for best model
    best_index = results_df['rank_test_balanced_accuracy'] == 1
    cv_scores = []
    for i in range(12):  # 4 splits * 3 repeats = 12
        score_key = f'split{i}_test_balanced_accuracy'
        if score_key in results_df.columns:
            cv_scores.extend(results_df[best_index][score_key])
    
    score_std = np.std(cv_scores) if cv_scores else np.nan
    
    # Get training and test scores
    train_scores = results_df[best_index]['mean_train_balanced_accuracy']
    test_scores = results_df[best_index]['mean_test_balanced_accuracy']
    score_diff = (train_scores - test_scores).abs().mean()
    
    # Log stability metrics
    logger.info(f"Cross-validation score standard deviation: {score_std:.4f}")
    logger.info(f"Train-test score difference: {score_diff:.4f}")
    
    # Warning thresholds
    if score_std > 0.1:
        logger.warning(f"High variance in CV scores detected (std={score_std:.4f})")
    if score_diff > 0.1:
        logger.warning(f"Potential overfitting detected (score difference={score_diff:.4f})")

def perform_grid_search(X: pd.DataFrame, y: pd.Series, param_grid: list, 
                       scoring: Dict[str, Any]) -> GridSearchCV:
    """
    Enhanced grid search with 4-fold CV and stability checks
    """
    lda = LinearDiscriminantAnalysis()
    
    cv = RepeatedStratifiedKFold(
        n_splits=4,
        n_repeats=3,
        random_state=42
    )
    
    grid_search = GridSearchCV(
        estimator=lda,
        param_grid=param_grid,
        scoring=scoring,
        cv=cv,
        n_jobs=-1,
        verbose=2,
        refit='balanced_accuracy',
        error_score=np.nan,
        return_train_score=True
    )
    
    try:
        # Check class balance
        class_counts = pd.Series(y).value_counts()
        min_class_size = class_counts.min()
        logger.info(f"Smallest class size: {min_class_size} samples")
        logger.info(f"Class distribution:\n{class_counts}")
            
        # Perform grid search
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            grid_search.fit(X, y)
            
            for warning in w:
                logger.warning(f"Warning during grid search: {warning.message}")
        
        check_model_stability(grid_search, X, y)
        return grid_search
        
    except Exception as e:
        logger.error(f"Grid search failed with error: {str(e)}")
        raise

def save_results(grid_search: GridSearchCV, output_folder: str = "tuning_results"):
    """
    Save comprehensive grid search results and analysis
    """
    os.makedirs(output_folder, exist_ok=True)
    results_df = pd.DataFrame(grid_search.cv_results_)
    
    # Save full results
    results_df.to_csv(os.path.join(output_folder, "all_results.csv"), index=False)
    
    # Save best parameters
    with open(os.path.join(output_folder, "best_parameters.txt"), "w") as f:
        f.write("Best Parameters:\n")
        for param, value in grid_search.best_params_.items():
            f.write(f"{param}: {value}\n")
        f.write(f"\nBest Score (Balanced Accuracy): {grid_search.best_score_:.4f}\n")
    
    # Save top 10 configurations
    top_10_idx = results_df['rank_test_balanced_accuracy'] <= 10
    top_10_results = results_df[top_10_idx].sort_values('rank_test_balanced_accuracy')
    top_10_results.to_csv(os.path.join(output_folder, "top_10_results.csv"), index=False)
    
    # Save detailed analysis
    best_idx = grid_search.best_index_
    with open(os.path.join(output_folder, "detailed_analysis.txt"), "w") as f:
        f.write("=== DETAILED ANALYSIS ===\n\n")
        
        # Best parameters
        f.write("Best Parameters:\n")
        f.write("-" * 50 + "\n")
        for param, value in grid_search.best_params_.items():
            f.write(f"{param}: {value}\n")
        
        # Performance metrics
        f.write("\nPerformance Metrics:\n")
        f.write("-" * 50 + "\n")
        for metric in ['balanced_accuracy', 'accuracy', 'precision_weighted', 
                      'recall_weighted', 'f1_weighted', 'mcc']:
            train_score = results_df[f'mean_train_{metric}'][best_idx]
            train_std = results_df[f'std_train_{metric}'][best_idx]
            test_score = results_df[f'mean_test_{metric}'][best_idx]
            test_std = results_df[f'std_test_{metric}'][best_idx]
            
            f.write(f"\n{metric.upper()}:\n")
            f.write(f"Training: {train_score:.4f} (±{train_std:.4f})\n")
            f.write(f"Testing:  {test_score:.4f} (±{test_std:.4f})\n")

def print_summary(grid_search: GridSearchCV):
    """
    Print concise summary of grid search results
    """
    print("\n=== HYPERPARAMETER TUNING SUMMARY ===")
    print("\nBest Parameters:")
    for param, value in grid_search.best_params_.items():
        print(f"{param:20}: {value}")
    
    print("\nPerformance Metrics:")
    best_idx = grid_search.best_index_
    results_df = pd.DataFrame(grid_search.cv_results_)
    
    for metric in ['balanced_accuracy', 'accuracy', 'precision_weighted', 
                  'recall_weighted', 'f1_weighted', 'mcc']:
        test_score = results_df[f'mean_test_{metric}'][best_idx]
        test_std = results_df[f'std_test_{metric}'][best_idx]
        print(f"{metric:20}: {test_score:.4f} (±{test_std:.4f})")

def main():
    try:
        start_time = time.time()
        logger.info("Starting LDA hyperparameter tuning")
        
        # Load and preprocess data
        print("Loading training data...")
        training_data = pd.read_csv(Training_filename, delimiter='\t')
        
        print("Normalizing data...")
        training_data = normalize_df(training_data.copy(), norm_threshold, training_data)
        
        if MMRF_DATA:
            code_six = (training_data.Code != 6) & (training_data.Code != 3)
            training_data = training_data[code_six]
        
        # Prepare features and target
        print("Preparing features and target...")
        X, y = prepare_lda_data(training_data)
        if X is None or y is None:
            raise ValueError("Error preparing features and target")
        y = y.values.ravel()
        
        # Setup hyperparameter tuning
        print("Setting up parameter grid and metrics...")
        param_grid = create_parameter_grid()
        scoring = create_scoring_metrics()
        
        # Perform grid search
        print("Starting grid search...")
        grid_search = perform_grid_search(X, y, param_grid, scoring)
        
        # Save and print results
        print("Saving results...")
        save_results(grid_search)
        print_summary(grid_search)
        
        # Save best model
        print("Saving best model...")
        os.makedirs(MODELS_FOLDER, exist_ok=True)
        joblib.dump(grid_search.best_estimator_, os.path.join(MODELS_FOLDER, pkl_filename))
        
        execution_time = time.time() - start_time
        print(f"\nTotal execution time: {execution_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()