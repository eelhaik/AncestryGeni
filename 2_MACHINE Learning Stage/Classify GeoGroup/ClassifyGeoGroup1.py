#ClassifyGeoGroup
# -*- coding: utf-8 -*-

"""
ClassifyGeoGroup

Description:
    ClassifyGeoGroup is a Python script designed for supervised machine learning (SML) classification of GeoGroup based on genomic data. The script utilizes Linear Discriminant Analysis (LDA) to classify Sample Reference Registry (SRR) values from input genomic features. Ancestral components, collapsed into five regions (Africa, East Asia, Europe, Central Asia, and America), serve as input features for the SML model.

This script reads a txt document with 5 GeoGroup classifiers and a code. It then trains an LDA classifier to classify the code. It will then be applied to other datasets.
 
Input:
    Training and testing data files containing genomic features and corresponding SRR values. These files should be tabular 
    format with columns representing ancestral components (features) and SRR values (target). The script expects these files 
    to be provided as arguments during execution.

Output:
    The script generates output files containing classified SRR values and performance metrics of the trained model. These output files provide insights into the accuracy and reliability of the model. Additionally, the script may produce visualization plots to aid in result interpretation.

Dependencies:
    - Python 3.x
    - NumPy
    - pandas
    - scikit-learn

Usage:
    python ClassifyGeoGroup.py <training_data_file> <testing_data_file>

Methodology:
    1. Data Preprocessing: Ancestral components are collapsed into five regions for simplicity. Data splitting is performed 
       to allocate samples for training, validation, and testing.
    2. Model Training: Linear Discriminant Analysis (LDA) is used to train the SML model on the training data. The model parameters, 
       including the maximum number of trees, are specified based on the requirements.
    3. Cross-Validation: The trained model is evaluated through 10-fold cross-validation to assess its performance and 
       generalization capabilities.
    4. Performance Evaluation: Performance metrics, such as accuracy and error rates, are computed to quantify the model's performance.
    5. Result Interpretation: classified SRR values and performance metrics are generated as output, facilitating result 
       interpretation and model refinement.

Based on: GPSEra_3

Race codes: 1=white, 2=black, 3=hispanic, 4=Asian, 6=other
----------------------------------------------------
Created by: Eran Elhaik and Sara Behnamian
Date: 22/10/23
Ver: 1.00
----------------------------------------------------
"""
import sys
import logging
import commentjson as json
import os
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import confusion_matrix
from module_preprocessor import DataPreprocessor  # assuming 'module_preprocessor.py' is in the local folder
from module_model_executor import ModelExecutor  # assuming 'module_model_executor.py' is in the local folder
from typing import Tuple, Optional
from sklearn.metrics import (accuracy_score, roc_auc_score, recall_score, 
                           precision_score, f1_score, cohen_kappa_score, 
                           matthews_corrcoef)
import time

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Configuration File
with open('config.json', 'r') as f:
    config = json.load(f)

# Define the input folder and other constants

#Training data
INPUT_TRAINING_FOLDER = config['INPUT_TRAINING_FOLDER']
INPUT_TRAINING_FILE = config['INPUT_TRAINING_FILE']
Training_filename = INPUT_TRAINING_FOLDER + '\\' + INPUT_TRAINING_FILE

#Testing data
INPUT_TESTING_FOLDER = config['INPUT_TESTING_FOLDER']
INPUT_TESTING_FILE = config['INPUT_TESTING_FILE']

#Model folders
MODELS_FOLDER = "./ML_models"
pkl_filename = 'best_model.pkl'

RESULTS_FOLDER = "./ML_results"

#Two types of gene pools are available for analysis
TRAINING_COLUMNS_BASIC = ['Africans', 'Asians', 'Europeans', 'Indians', 'NativeAmericans']
TRAINING_COLUMNS_FULL = ['Z_Africa1', 'Z_Africa2', 'Z_CentralAsia', 'Z_CentralEurope', 'Z_EastAsia', 'Z_FarEastAsia', 'Z_India', 'Z_NativeAmerica', 'Z_Scandinavia', 'Z_SouthEastAsia', 'Z_SouthEurope', 'Z_UK']
TRAINING_COLUMNS = TRAINING_COLUMNS_FULL
#TRAINING_COLUMNS = TRAINING_COLUMNS_BASIC


TARGET_COLUMN = ['Code']
PERFORMANCE_XLSX_PATH = "best_performance_metrics.xlsx"  # Change this as needed during runtime

MMRF_DATA = config['MMRF_DATA']
SPLIT_DATA = config['SPLIT_DATA']
COLS = config['COLS']
N_SPLITS = config['N_SPLITS']

#zero all cells smaller than threshold
norm_threshold = 0.1

def initialize_ML_models():
    """
    Initialize machine learning models for training.
    Called by TrainPredictor.

    Returns:
    - models (dict): Dictionary containing initialized machine learning models.

    """    
    return {
        'LDA': {'model': LinearDiscriminantAnalysis, 'use': True},

    }

def TrainClassifier(data_file, folder_suffix):
    """
    Train classifier models using the provided data file and save the trained models as .pkl files.
    Also, save performance metrics to an Excel file.

    Parameters:
    - data_file (str): The name of the data file to be used for training.
    - folder_suffix (str): The suffix for the folder where the models will be saved.

    Returns:
    - pkl_model_filename (str): The file path of the saved model .pkl file.

    Note:
    The function assumes the existence of constants like MODELS_FOLDER, RESULTS_FOLDER, TARGET_COLUMN, TRAINING_COLUMNS,
    and initializes models using available_ML_models() function.
    """
    
    try:
        os.makedirs(MODELS_FOLDER, exist_ok=True)
        os.makedirs(RESULTS_FOLDER, exist_ok=True)

        # Define model save path
        pkl_model_filename = os.path.join(MODELS_FOLDER, pkl_filename)
        pkl_model_filename = pkl_model_filename.replace('\\', '/')

        # Data Loading Phase
        logger.info(f"Starting the data loading phase for {folder_suffix}.")

        data_filename = folder_suffix + '\\' + data_file
        raw_data = pd.read_csv(data_filename, delimiter='\t')

        #Identify the gene pools
        training_cols = list(set(raw_data.columns) - set(TARGET_COLUMN))

        # Data Preprocessing Phase
        logger.info(f"Starting the data preprocessing phase for {folder_suffix}.")
        data_preprocessor = DataPreprocessor(raw_data, TRAINING_COLUMNS + TARGET_COLUMN)
        data_preprocessor.apply_pipeline()
        processed_data = data_preprocessor.get_data()

        # Initialize models
        available_models = initialize_ML_models()

        # Create folders if not exist
        os.makedirs(RESULTS_FOLDER, exist_ok=True)
        os.makedirs(MODELS_FOLDER, exist_ok=True)

        # Model Execution Phase - saving .pkl file
        logger.info(f"Starting the model execution phase for {MODELS_FOLDER}.")
        
        executor = ModelExecutor(model_dict=available_models, model_save_path=pkl_model_filename)
        executor.execute(processed_data, training_cols, TARGET_COLUMN, folder_suffix)

        # Save Performance Metrics to Excel
        name_excel = os.path.join(RESULTS_FOLDER, f"{PERFORMANCE_XLSX_PATH}")
        print('Output filename:', name_excel)

        #Define the df of the results
        df = pd.DataFrame.from_dict({
            (i, j): executor.results[i][j]
            for i in executor.results.keys()
            for j in executor.results[i].keys()
        }, orient='index')
           
        #Save the df results to the excel
        print('Saving reuslts as:', name_excel)
        df.to_excel(name_excel, index=True)

        logger.info(f"Pipeline executed successfully for {folder_suffix}.")

        return pkl_model_filename

    except Exception as e:
        logger.error(f"An exception occurred during pipeline execution for {folder_suffix}: {e}")
        
#Prepare the feature and target matrices for LDA training
def prepare_lda_data(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Prepare the feature matrix and target vector for training a Linear Discriminant Analysis classifier.

    Parameters:
    - df (DataFrame): The input DataFrame containing features and target column.

    Returns:
    - Tuple containing feature matrix and target vector.
    """    
    try:
        #Retain the features and target code
        features = df[TRAINING_COLUMNS]
        target = df[COLS['TARGET']] #Target dataset

        return features, target
    except KeyError as e:
        logging.error(f"KeyError encountered: {e}")
        return None, None


def evaluate_model(model: LinearDiscriminantAnalysis, X_test: pd.DataFrame, y_test: pd.DataFrame) -> dict:
    """
    Evaluate the LDA classifier using multiple classification metrics.

    Parameters:
    - model: Trained LinearDiscriminantAnalysis model
    - X_test: Test features
    - y_test: True test labels

    Returns:
    - Dictionary containing various classification metrics
    """    
    try:
        start_time = time.time()
        y_class = model.predict(X_test)
        
        # Calculate probabilities for AUC if available
        try:
            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_test)
                auc = roc_auc_score(y_test, y_prob, multi_class="ovr")
            else:
                auc = np.nan
        except Exception:
            auc = np.nan

        # Calculate multiple classification metrics
        metrics = {
            'Accuracy': accuracy_score(y_test, y_class),
            'AUC': auc,
            'Recall': recall_score(y_test, y_class, average='weighted'),
            'Precision': precision_score(y_test, y_class, average='weighted'),
            'F1': f1_score(y_test, y_class, average='weighted'),
            'Kappa': cohen_kappa_score(y_test, y_class),
            'MCC': matthews_corrcoef(y_test, y_class),
            'Training_Time': round(time.time() - start_time, 4)
        }
        
        # Log the results
        logger.info("LDA Classification Metrics:")
        for metric, value in metrics.items():
            logger.info(f"{metric}: {value}")
            
        return metrics
        
    except Exception as e:
        logger.error(f"Error in LDA evaluation: {e}")
        return None
    

def execute_lda_model(X, y):
    """
    Executes a Linear Discriminant Analysis (LDA) model for classification.

    Args:
        X (pandas.DataFrame): Input features for training.
        y (numpy.ndarray): Target variable for training.

    Returns:
        sklearn.discriminant_analysis.LinearDiscriminantAnalysis: The best classification model based on accuracy.

    Raises:
        ValueError: If an error occurs during data splitting.

    Note:
        This function splits the data into training and test sets using stratified shuffle splitting with a 
        specified number of splits (N_SPLITS). It trains multiple LDA models on different subsets of the data and 
        selects the best model based on accuracy.

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

                    # Save the best model based on accuracy
                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_model = model

            # Save the best model after finding it
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
    Train a Linear Discriminant Analysis (LDA) classifier with optimized parameters.

    Parameters:
    - X (array-like): The input features for training.
    - y (array-like): The true labels.

    Returns:
    - classifier: Trained LDA classifier.
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
    Evaluate the performance of a classifier model using accuracy score.

    Parameters:
    - model: The trained classifier model.
    - X (array-like): The input features for classification.
    - y (array-like): The true labels.

    Returns:
    - accuracy (float): Accuracy score of the classifier model.
    """    
    y_class = model.predict(X)
    accuracy = accuracy_score(y, y_class)
    return accuracy


def classify_code(df, best_model, X):
    """
    Generate classifications using the best model and append the classified codes to the DataFrame.

    Parameters:
    - df (DataFrame): The DataFrame containing the dataset.
    - best_model: The trained model used for making classifications.
    - X (array-like): The input features for classification.

    Returns:
    - df (DataFrame): The DataFrame with the classified codes appended as a new column.
    """    
    # Generate classifications for the entire dataset
    #print('Generate classifications')
    classifications = best_model.predict(X)  # Assuming classifications are categorical labels
    df['classified_code'] = classifications
    #print('Classifications completed')

    return df

def normalize_df(df, threshold, Training_dataset_df):
    """
    Normalize the given DataFrame by thresholding, setting all values smaller than the threshold to zero,
    and then normalizing each row to sum up to 1. If the threshold is too high and the array has NaNs,
    the function will recursively call itself with a lower threshold until all NaNs are removed.

    Parameters:
    - df (DataFrame): The DataFrame to be normalized.
    - threshold (float): The threshold value below which values are set to zero.
    - Training_dataset_df (DataFrame): The original training dataset DataFrame, used for recursive calls.

    Returns:
    - df (DataFrame): The normalized DataFrame.
    """
    
    #print('In normalize_df, with threshold=', threshold)
    #print(df)

    # Rounding values less than the threshold to 0
    #df.iloc[:, :-1] = df.iloc[:, :-1].applymap(lambda x: 0 if x < threshold else x)
    df[TRAINING_COLUMNS] = df[TRAINING_COLUMNS].map(lambda x: 0 if (isinstance(x, str) or x < threshold) else x)

    # Normalize each row to sum to 1
    #row_sums = df.iloc[:, :-1].sum(axis=1)
    #df.iloc[:, :-1] = df.iloc[:, :-1].div(row_sums, axis=0)

    # Normalize each row to sum to 1
    row_sums = df[TRAINING_COLUMNS].sum(axis=1)
    df[TRAINING_COLUMNS] = df[TRAINING_COLUMNS].div(row_sums, axis=0)
    
    # Check for NaN values in the DataFrame
    #it happens if all the cells are < threshold so they become NaN
    has_nan = df[TRAINING_COLUMNS].isna().any().any()

    if has_nan:
        print("DataFrame contains NaN values, calling the function again with threshold", threshold - 0.01)
        rows_with_nan = df[df[TRAINING_COLUMNS].isna().any(axis=1)]
        #print(rows_with_nan)      
        
        threshold -= 0.01
        print('Calling the function with', threshold)
        #print(df)
        #input()
        df = normalize_df(Training_dataset_df.copy(), threshold, Training_dataset_df)
    else:
        print("DataFrame does NOT contain any NaN values.")

    return df


def calculate_accuracy(conf_matrix):
    """
    Calculate the accuracy of a classification model based on a given confusion matrix.

    Parameters:
    - conf_matrix (list of lists): Confusion matrix representing the classification results.
                                   Rows correspond to actual classes, columns correspond to classified classes.

    Returns:
    - accuracy (float): Accuracy of the classification model, defined as the ratio of correct classifications to total classifications.
    """    
    correct_classifications = sum(conf_matrix[i][i] for i in range(len(conf_matrix)))
    total_classifications = sum(sum(row) for row in conf_matrix)
    accuracy = correct_classifications / total_classifications
    return accuracy


def print_confusion_matrix_basic(observed_codes, classified_codes, output_file):
    """
    Prints the confusion matrix based on the actual and classified codes.

    Parameters:
        observed_codes (list): List of actual codes.
        classified_codes (list): List of classified codes.

    Returns:
        None
    """
    # Extract unique codes from observed_codes
    unique_codes = sorted(set(observed_codes))
    
    # Calculate confusion matrix
    conf_matrix = confusion_matrix(observed_codes, classified_codes)
    
    # Print headers
    header = "Actual \\ Classified".ljust(12) + "\t".join(str(code).center(8) for code in unique_codes)
    print(header)
    print("\t" + "-" * len(header))
    
    # Print confusion matrix
    for i, row in enumerate(conf_matrix):
        print(f"{unique_codes[i]:<12}" + "\t".join(f"{count:^8}" for count in row))

    
    # Print confusion matrix with tab-delimited numbers only
    print("\nConfusion Matrix (Tab-Delimited):")
    for row in conf_matrix:
        print("\t".join(str(count) for count in row))

    accuracy = calculate_accuracy(conf_matrix)
    print(f"Accuracy: {accuracy:.2f}")

    #Write to file
        
    # Print confusion matrix with tab-delimited numbers only
    for row in conf_matrix:
        output_file.write("\t".join(str(count) for count in row) + '\n')

    # Calculate accuracy
    accuracy = calculate_accuracy(conf_matrix)
    output_file.write(f"Accuracy: {accuracy:.2f}\n")


def print_detailed_metrics(observed_codes, classified_codes, model, X_test, y_test, output_file):
    """
    Prints detailed metrics including confusion matrix and all evaluation metrics.
    """
    # Get all metrics using existing evaluate_model function
    metrics = evaluate_model(model, X_test, y_test)
    
    # Print and write section separator
    section_separator = "\n" + "="*50 + "\n"
    output_file.write(section_separator)
    
    # Print confusion matrix with labels
    unique_codes = sorted(set(observed_codes))
    conf_matrix = confusion_matrix(observed_codes, classified_codes)
    
    output_file.write("CONFUSION MATRIX:\n")
    
    # Matrix header
    matrix_header = "Actual \\ classified".ljust(12) + "\t".join(str(code).center(8) for code in unique_codes)
    output_file.write(matrix_header + "\n")
    output_file.write("-" * len(matrix_header) + "\n")
    
    # Matrix content
    for i, row in enumerate(conf_matrix):
        line = f"{unique_codes[i]:<12}" + "\t".join(f"{count:^8}" for count in row)
        output_file.write(line + "\n")
    
    # Print metrics
    output_file.write(f"{section_separator}CLASSIFICATION METRICS:\n")
    
    if metrics:
        for metric, value in metrics.items():
            formatted_line = f"{metric:<20}: {value:>10.4f}"
            output_file.write(formatted_line + "\n")
    
    output_file.write(section_separator)
  
def main():
    print('Start program: ClassifyRace')
    os.makedirs(MODELS_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    
    # TRAINING #
    print('\nLoad training filename...')
    Training_dataset_df = pd.read_csv(Training_filename, delimiter='\t')
    
    # Normalize
    Training_dataset_df = normalize_df(Training_dataset_df.copy(), norm_threshold, Training_dataset_df)
   

    if MMRF_DATA:
        #Remove 6 from the training data
        #Remove also 3 because there are no asians in the MMRF data
        code_six = (Training_dataset_df.Code != 6) & (Training_dataset_df.Code != 3)
        Training_dataset_df = Training_dataset_df[code_six]
    
    # Create an array with 50% True values followed by 50% False values
    if SPLIT_DATA:
        print('\nTraining on 50% of the data...')
        boolean_array = np.random.choice([True, False], size=len(Training_dataset_df), p=[0.5, 0.5])
        Training_dataset_df = Training_dataset_df[boolean_array]


    # Create train/test split using stratified sampling
    print('\nCreating train/test split...')
    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, _ = next(sss.split(Training_dataset_df, Training_dataset_df['Code']))
    
    # Save training portion
    train_data = Training_dataset_df.iloc[train_idx]
    train_file_path = os.path.join(RESULTS_FOLDER, "training_set.csv")
    train_data.to_csv(train_file_path, sep='\t', index=False)
    print(f"Saved training set with {len(train_data)} samples to {train_file_path}")
    
    # Update Training_dataset_df to only include training data
    Training_dataset_df = train_data

    # Process and save test datasets
    print('\nProcessing test files...')
    for test_file in INPUT_TESTING_FILE:
        print(f"\nProcessing test file: {test_file}")
        Testing_file = os.path.join(INPUT_TESTING_FOLDER, test_file)
        
        # Load and normalize test data
        Testing_dataset_df = pd.read_csv(Testing_file, delimiter='\t')
        Testing_dataset_df = normalize_df(Testing_dataset_df.copy(), norm_threshold, Training_dataset_df)

        if MMRF_DATA:
            # Remove 6 and 3 from test data
            code_six = (Testing_dataset_df.Code != 6) & (Testing_dataset_df.Code != 3)
            Testing_dataset_df = Testing_dataset_df[code_six]
        
        # Remove samples that were in training
        Testing_dataset_df = Testing_dataset_df[~Testing_dataset_df['SampleCode'].isin(Training_dataset_df['SampleCode'])]
        
        # # Save filtered test dataset
        # test_file_name = os.path.splitext(test_file)[0]
        # test_output_path = os.path.join(RESULTS_FOLDER, f"test_{test_file_name}.csv")
        # Testing_dataset_df.to_csv(test_output_path, sep='\t', index=False)
        # print(f"Saved test file {test_file_name} with {len(Testing_dataset_df)} samples to {test_output_path}")

    # Model Training
    print('\nPreparing data for LDA')
    X, y = prepare_lda_data(Training_dataset_df)
    y = y.values.ravel()  # Flatten y to be a 1D array

    # Execute LDA model
    print('Training LDA model...')
    best_model = execute_lda_model(X, y)

    print('QC on best model = ', best_model)
    if best_model is None:
        print('main() Error: best_model is None')
        sys.exit(1)

    # Model Evaluation
    print('\nEvaluating model...')
    with open(os.path.join(RESULTS_FOLDER, 'output_basic.txt'), "w") as output_file_basic, \
         open(os.path.join(RESULTS_FOLDER, 'output_detailed.txt'), "w") as output_file_detailed:
        
        # for INPUT_TESTING_FILE_curr in INPUT_TESTING_FILE:
        #     print(f"\nProcessing test file: {INPUT_TESTING_FILE_curr}")
        #     Testing_file = os.path.join(INPUT_TESTING_FOLDER, INPUT_TESTING_FILE_curr)
        for test_file in INPUT_TESTING_FILE:
            print(f"\nProcessing test file: {test_file}")
            Testing_file = os.path.join(INPUT_TESTING_FOLDER, test_file)
            
            # Save the corresponding training set for the current test file
            training_pair_path = os.path.join(RESULTS_FOLDER, f"training_pair_for_{os.path.splitext(test_file)[0]}.csv")
            Training_dataset_df.to_csv(training_pair_path, sep='\t', index=False)
            print(f"Saved training pair for test file {test_file} to {training_pair_path}")

            
            # Load and preprocess test data
            Testing_dataset_df = pd.read_csv(Testing_file, delimiter='\t')
            Testing_dataset_df = normalize_df(Testing_dataset_df.copy(), norm_threshold, Testing_dataset_df)

            if MMRF_DATA:
                code_six = (Testing_dataset_df.Code != 6) & (Testing_dataset_df.Code != 3)
                Testing_dataset_df = Testing_dataset_df[code_six]
            
            # Remove training samples
            Testing_dataset_df = Testing_dataset_df[~Testing_dataset_df['SampleCode'].isin(Training_dataset_df['SampleCode'])]

            if Testing_dataset_df.empty:
                print(f"Warning: No samples remaining in {INPUT_TESTING_FILE_curr} after filtering")
                continue

            # Prepare test data for classification
            X_pred, Y_pred = prepare_lda_data(Testing_dataset_df)
            
            # Make classifications
            df_code_pred = classify_code(Testing_dataset_df.copy(), best_model, X_pred)

            # Save test data with classifications
            test_file_name = os.path.splitext(test_file)[0]
            test_output_path = os.path.join(RESULTS_FOLDER, f"test_{test_file_name}_with_classifications.csv")
            df_code_pred.to_csv(test_output_path, sep='\t', index=False)
            print(f"Saved test file with classification results to {test_output_path}")
            
            # Generate evaluation metrics
            print_confusion_matrix_basic(
                df_code_pred['Code'],
                df_code_pred['classified_code'],
                output_file_basic
            )
            
            print_detailed_metrics(
                df_code_pred['Code'],
                df_code_pred['classified_code'],
                best_model,
                X_pred,
                Y_pred,
                output_file_detailed
            )

    # Save final results
    print('\nEnd program: classifyRace')

if __name__ == '__main__':
    main()
