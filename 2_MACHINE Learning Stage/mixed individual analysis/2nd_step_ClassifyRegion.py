import sys
import logging
import os
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import confusion_matrix
from typing import Tuple, Optional
from sklearn.metrics import (accuracy_score, roc_auc_score, recall_score, 
                           precision_score, f1_score, cohen_kappa_score, 
                           matthews_corrcoef)
import time

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MODELS_FOLDER = "./ML_models"
RESULTS_FOLDER = "./ML_results"
pkl_filename = 'best_model.pkl'

# Define the columns matching your Excel file
TRAINING_COLUMNS = [
    'Africa1', 'Africa2', 'CentralAsia', 'CentralEurope', 
    'EastAsia', 'FarEastAsia', 'India', 'NativeAmerica',
    'Scandinavia', 'SouthEastAsia', 'SouthEurope', 'UK'
]

TARGET_COLUMN = ['Region']
PERFORMANCE_XLSX_PATH = "best_performance_metrics.xlsx"

# Configuration parameters
N_SPLITS = 5
norm_threshold = 0.1

def initialize_ML_models():
    """
    Initialize machine learning models for training.
    """    
    return {
        'LDA': {'model': LinearDiscriminantAnalysis, 'use': True},
    }

def prepare_lda_data(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Prepare the feature matrix and target vector for LDA.
    """    
    try:
        features = df[TRAINING_COLUMNS]
        target = df[TARGET_COLUMN]
        return features, target
    except KeyError as e:
        logging.error(f"KeyError encountered: {e}")
        return None, None

def evaluate_model(model: LinearDiscriminantAnalysis, X_test: pd.DataFrame, y_test: pd.DataFrame) -> dict:
    """
    Evaluate the LDA classifier using multiple classification metrics.
    """    
    try:
        start_time = time.time()
        y_pred = model.predict(X_test)
        
        # Calculate probabilities for AUC
        try:
            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_test)
                # One-vs-Rest ROC AUC for each class
                auc_scores = []
                for i in range(len(model.classes_)):
                    # Create binary labels for current class
                    y_test_binary = (y_test == model.classes_[i]).astype(int)
                    auc_scores.append(roc_auc_score(y_test_binary, y_prob[:, i]))
                # Average AUC across all classes
                auc = np.mean(auc_scores)
            else:
                auc = np.nan
        except Exception as e:
            logger.error(f"Error calculating AUC: {e}")
            auc = np.nan

        # Calculate multiple classification metrics
        metrics = {
            'Accuracy': accuracy_score(y_test, y_pred),
            'AUC': auc,
            'Recall': recall_score(y_test, y_pred, average='weighted'),
            'Precision': precision_score(y_test, y_pred, average='weighted'),
            'F1': f1_score(y_test, y_pred, average='weighted'),
            'Kappa': cohen_kappa_score(y_test, y_pred),
            'MCC': matthews_corrcoef(y_test, y_pred),
            'Training_Time': round(time.time() - start_time, 4)
        }
        
        logger.info("LDA Classification Metrics:")
        for metric, value in metrics.items():
            logger.info(f"{metric}: {value}")
            
        return metrics
        
    except Exception as e:
        logger.error(f"Error in LDA evaluation: {e}")
        return None

def execute_lda_model(X, y):
    """
    Execute LDA model with cross-validation.
    """
    print("Executing LDA model for classification...")

    best_model = None
    best_accuracy = 0.0

    if X is not None and y is not None:
        try:
            sss = StratifiedShuffleSplit(n_splits=N_SPLITS, test_size=0.2, random_state=42)
            for train_index, test_index in sss.split(X, y):
                X_train, X_test = X.iloc[train_index], X.iloc[test_index]
                y_train, y_test = y[train_index], y[test_index]

                model = train_lda_classifier(X_train, y_train)
                if model:
                    accuracy = evaluate_classifier(model, X_test, y_test)

                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_model = model

            if best_model is not None:
                joblib.dump(best_model, os.path.join(MODELS_FOLDER, pkl_filename))

        except ValueError as e:
            logging.error(f"Stratified Shuffle Split error: {e}")
            raise ValueError(f"Stratified Shuffle Split error: {e}")

    print("Returning the best classification model.")
    logging.info(f"Best classification model has accuracy: {best_accuracy}")

    return best_model

def train_lda_classifier(X, y):
    """
    Train LDA classifier with default parameters.
    """
    classifier = LinearDiscriminantAnalysis(#solver='svd'  # Default solver, explicitly stated here
    # solver='lsqr',          # Best solver from tuning
    # shrinkage='auto',       # Best shrinkage from tuning
    # store_covariance=True,  # Best from tuning
    # tol=1e-4               # Best tolerance from tuning (0.0001)
)
    classifier.fit(X, y)
    return classifier

def evaluate_classifier(model, X, y):
    """
    Evaluate classifier using accuracy score.
    """    
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    return accuracy

def classify_code(df, best_model, X):
    """
    Generate classifications and append to DataFrame.
    """    
    classifications = best_model.predict(X)
    df['classified_region'] = classifications
    return df

def normalize_df(df, threshold, Training_dataset_df):
    """
    Normalize DataFrame with thresholding.
    """    
    # Convert comma decimals to periods first
    for col in TRAINING_COLUMNS:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '.').astype(float)
    
    df[TRAINING_COLUMNS] = df[TRAINING_COLUMNS].map(lambda x: 0 if (isinstance(x, str) or x < threshold) else x)
    
    row_sums = df[TRAINING_COLUMNS].sum(axis=1)
    df[TRAINING_COLUMNS] = df[TRAINING_COLUMNS].div(row_sums, axis=0)
    
    has_nan = df[TRAINING_COLUMNS].isna().any().any()

    if has_nan:
        print(f"DataFrame contains NaN values, adjusting threshold to {threshold - 0.01}")
        threshold -= 0.01
        df = normalize_df(Training_dataset_df.copy(), threshold, Training_dataset_df)
    else:
        print("DataFrame does NOT contain any NaN values.")

    return df

def calculate_accuracy(conf_matrix):
    """
    Calculate accuracy from confusion matrix.
    """    
    correct_classifications = sum(conf_matrix[i][i] for i in range(len(conf_matrix)))
    total_classifications = sum(sum(row) for row in conf_matrix)
    return correct_classifications / total_classifications

def print_confusion_matrix_basic(observed_codes, classified_codes, output_file):
    """
    Print basic confusion matrix.
    """
    unique_codes = sorted(set(observed_codes))
    conf_matrix = confusion_matrix(observed_codes, classified_codes)
    
    header = "Actual \\ Classified".ljust(12) + "\t".join(str(code).center(8) for code in unique_codes)
    print(header)
    print("\t" + "-" * len(header))
    
    for i, row in enumerate(conf_matrix):
        print(f"{unique_codes[i]:<12}" + "\t".join(f"{count:^8}" for count in row))

    print("\nConfusion Matrix (Tab-Delimited):")
    for row in conf_matrix:
        print("\t".join(str(count) for count in row))

    accuracy = calculate_accuracy(conf_matrix)
    print(f"Accuracy: {accuracy:.2f}")

    for row in conf_matrix:
        output_file.write("\t".join(str(count) for count in row) + '\n')

    output_file.write(f"Accuracy: {accuracy:.2f}\n")

def print_detailed_metrics(observed_codes, classified_codes, model, X_test, y_test, output_file):
    """
    Print detailed metrics and confusion matrix.
    """
    metrics = evaluate_model(model, X_test, y_test)
    
    section_separator = "\n" + "="*50 + "\n"
    output_file.write(section_separator)
    
    unique_codes = sorted(set(observed_codes))
    conf_matrix = confusion_matrix(observed_codes, classified_codes)
    
    output_file.write("CONFUSION MATRIX:\n")
    matrix_header = "Actual \\ Classified".ljust(12) + "\t".join(str(code).center(8) for code in unique_codes)
    output_file.write(matrix_header + "\n")
    output_file.write("-" * len(matrix_header) + "\n")
    
    for i, row in enumerate(conf_matrix):
        line = f"{unique_codes[i]:<12}" + "\t".join(f"{count:^8}" for count in row)
        output_file.write(line + "\n")
    
    output_file.write(f"{section_separator}CLASSIFICATION METRICS:\n")
    
    if metrics:
        for metric, value in metrics.items():
            formatted_line = f"{metric:<20}: {value:>10.4f}"
            output_file.write(formatted_line + "\n")
    
    output_file.write(section_separator)

def main():
    print('Start program: ClassifyRegions')
    os.makedirs(MODELS_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    
    # Load data
    print('\nLoad Excel file...')
    df = pd.read_excel("HGDP_Res_Updated.xlsx")
    
    # Normalize
    df = normalize_df(df.copy(), norm_threshold, df)
    
    # Create train/test split
    print('\nCreating train/test split...')
    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(sss.split(df, df['Region']))
    
    # Save training and testing portions
    train_data = df.iloc[train_idx]
    test_data = df.iloc[test_idx]
    
    train_file_path = os.path.join(RESULTS_FOLDER, "training_set.xlsx")
    test_file_path = os.path.join(RESULTS_FOLDER, "testing_set.xlsx")
    
    train_data.to_excel(train_file_path, index=False)
    test_data.to_excel(test_file_path, index=False)
    print(f"Saved training set ({len(train_data)} samples) and testing set ({len(test_data)} samples)")

    # Model Training
    print('\nPreparing data for LDA')
    X, y = prepare_lda_data(train_data)
    y = y.values.ravel()

    # Execute LDA model
    print('Training LDA model...')
    best_model = execute_lda_model(X, y)

    if best_model is None:
        print('main() Error: best_model is None')
        sys.exit(1)

    # Model Evaluation
    print('\nEvaluating model...')
    with open(os.path.join(RESULTS_FOLDER, 'output_basic.txt'), "w") as output_file_basic, \
         open(os.path.join(RESULTS_FOLDER, 'output_detailed.txt'), "w") as output_file_detailed:
        
        X_test = test_data[TRAINING_COLUMNS]
        y_test = test_data[TARGET_COLUMN]
        
        # Make classifications
        df_class = classify_code(test_data.copy(), best_model, X_test)
        
        # Save classifications
        classifications_path = os.path.join(RESULTS_FOLDER, "classifications.xlsx")
        df_class.to_excel(classifications_path, index=False)
        print(f"Saved classifications to {classifications_path}")
        
        # Generate evaluation metrics
        print_confusion_matrix_basic(
            df_class['Region'],
            df_class['classified_region'],
            output_file_basic
        )
        
        print_detailed_metrics(
            df_class['Region'],
            df_class['classified_region'],
            best_model,
            X_test,
            y_test,
            output_file_detailed
        )

        # Save performance metrics to Excel
        metrics_df = pd.DataFrame(columns=['Metric', 'Value'])
        if y_test is not None:
            metrics = evaluate_model(best_model, X_test, y_test)
            if metrics:
                metrics_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
                metrics_xlsx_path = os.path.join(RESULTS_FOLDER, PERFORMANCE_XLSX_PATH)
                metrics_df.to_excel(metrics_xlsx_path, index=False)
                print(f"Saved performance metrics to {metrics_xlsx_path}")

    print('\nEnd program: ClassifyRegions')

if __name__ == '__main__':
    main()