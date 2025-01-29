#PredictContinentalPopulations
# -*- coding: utf-8 -*-

"""
PredictContinentalPopulations

Description:
    PredictContinentalPopulations is a Python script designed for supervised machine learning (SML) prediction of Continental Populations based on genomic data. The script utilizes random forest regression to predict Sample Reference Registry (SRR) values from input genomic features. Ancestral components, collapsed into five regions (Africa, East Asia, Europe, Central Asia, and America), serve as input features for the SML model.

This script reads a txt document with 5 racial classifiers and a code. It then trains a Random forest to predict the code. It will then be applied to other datasets.
 
Input:
    Training and testing data files containing genomic features and corresponding SRR values. These files should be tabular 
    format with columns representing ancestral components (features) and SRR values (target). The script expects these files 
    to be provided as arguments during execution.

Output:
    The script generates output files containing predicted SRR values and performance metrics of the trained model. These output files provide insights into the accuracy and reliability of the model predictions. Additionally, the script may produce visualization plots to aid in result interpretation.

Dependencies:
    - Python 3.x
    - NumPy
    - pandas
    - scikit-learn

Usage:
    python PredictContinentalPopulations.py 

Methodology:
    1. Data Preprocessing: Ancestral components are collapsed into five regions for simplicity. Data splitting is performed 
       to allocate samples for training, validation, and testing.
    2. Model Training: Random forest regression is used to train the SML model on the training data. The model parameters, 
       including the maximum number of trees, are specified based on the requirements.
    3. Cross-Validation: The trained model is evaluated through 10-fold cross-validation to assess its performance and 
       generalization capabilities.
    4. Performance Evaluation: Performance metrics, such as accuracy and error rates, are computed to quantify the model's 
       predictive performance.
    5. Result Interpretation: Predicted SRR values and performance metrics are generated as output, facilitating result 
       interpretation and model refinement.

Continental codes: 1=white, 2=black, 3=hispanic, 4=Asian, 6=other
Functions:
----------------------------------------------------
Created by: Eran Elhaik
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
#import joblib
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import confusion_matrix

from module_preprocessor import DataPreprocessor  # assuming 'module_preprocessor.py' is in the local folder
from module_model_executor import ModelExecutor  # assuming 'module_model_executor.py' is in the local folder
from typing import Tuple, Optional

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Configuration File
with open('config_CP.json', 'r') as f:
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
        'RandomForest': {'model': RandomForestClassifier, 'use': True},
#        'GradientBoost': {'model': GradientBoostingRegressor, 'use': True},
#        'XGBoost': {'model': XGBRegressor, 'use': True},
#        'lightgbm': {'model': lgb.LGBMRegressor, 'use': True},
    }
#Not called

def TrainPredictor(data_file, folder_suffix):
    """
    Train predictor models using the provided data file and save the trained models as .pkl files.
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
        # Create directory for saving the model .pkl file
        pkl_model_filename = os.path.join(MODELS_FOLDER, pkl_filename)
        pkl_model_filename = pkl_model_filename.replace('\\', '/')

        #Create folder
        if not os.path.exists(pkl_model_filename):
            os.makedirs(pkl_model_filename)

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
        

#Prepare the feature and target matrices for Random Forest training
def prepare_rf_data(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Prepare the feature matrix and target vector for training a Random Forest classifier.

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
        
'''
#Evaluate the RF model
def evaluate_model(model: RandomForestRegressor, X_test: pd.DataFrame, y_test: pd.DataFrame) -> float:
    try:
        r2_test = r2_score(y_test, model.predict(X_test))
        logging.info(f"Random Forest R2 score_test: {r2_test}")
        return r2_test
    except Exception as e:
        logging.error(f"Error in Random Forest evaluation: {e}")
        return float('-inf')  # Return negative infinity if evaluation fails
'''

# Run the RF model
def execute_rf_model(X, y):
    """
    Executes a Random Forest (RF) model for classification.

    Args:
        X (pandas.DataFrame): Input features for training.
        y (numpy.ndarray): Target variable for training.

    Returns:
        sklearn.ensemble.RandomForestClassifier: The best classification model based on accuracy.

    Raises:
        ValueError: If an error occurs during data splitting.

    Note:
        This function splits the data into training and test sets using stratified shuffle splitting with a 
        specified number of splits (N_SPLITS). It trains multiple RF models on different subsets of the data and 
        selects the best model based on accuracy.

    """
    print("Executing RF model for classification...")

    best_model = None
    best_accuracy = 0.0

    if X is not None and y is not None:
        try:
            sss = StratifiedShuffleSplit(n_splits=N_SPLITS, test_size=0.2, random_state=42)
            for train_index, test_index in sss.split(X, y):
                X_train, X_test = X.iloc[train_index], X.iloc[test_index]
                y_train, y_test = y[train_index], y[test_index]

                model = train_random_forest_classifier(X_train, y_train)
                if model:
                    accuracy = evaluate_classifier(model, X_test, y_test)

                    # Save the best model based on accuracy
                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_model = model

        except ValueError as e:
            logging.error(f"Stratified Shuffle Split error: {e}")
            raise ValueError(f"Stratified Shuffle Split error: {e}")

    print("Returning the best classification model.")
    logging.info(f"Best classification model has accuracy: {best_accuracy}")

    return best_model


def train_random_forest_classifier(X, y):
    """
    Train a Random Forest classifier using 100 decision trees.

    Parameters:
    - X (array-like): The input features for training.
    - y (array-like): The true labels.

    Returns:
    - classifier: Trained Random Forest classifier.
    """
    classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    classifier.fit(X, y)
    return classifier


def evaluate_classifier(model, X, y):
    """
    Evaluate the performance of a classifier model using accuracy score.

    Parameters:
    - model: The trained classifier model.
    - X (array-like): The input features for prediction.
    - y (array-like): The true labels.

    Returns:
    - accuracy (float): Accuracy score of the classifier model.
    """    
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    return accuracy


def predict_code(df, best_model, X):
    """
    Generate predictions using the best model and append the predicted codes to the DataFrame.

    Parameters:
    - df (DataFrame): The DataFrame containing the dataset.
    - best_model: The trained model used for making predictions.
    - X (array-like): The input features for prediction.

    Returns:
    - df (DataFrame): The DataFrame with the predicted codes appended as a new column.
    """    
    # Generate predictions for the entire dataset
    #print('Generate predictions')
    predictions = best_model.predict(X)  # Assuming predictions are categorical labels
    df['predicted_code'] = predictions
    #print('Predictions completed')

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
    df[TRAINING_COLUMNS] = df[TRAINING_COLUMNS].applymap(lambda x: 0 if (isinstance(x, str) or x < threshold) else x)

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
        #rows_with_nan = df[df[TRAINING_COLUMNS].isna().any(axis=1)]
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
                                   Rows correspond to actual classes, columns correspond to predicted classes.

    Returns:
    - accuracy (float): Accuracy of the classification model, defined as the ratio of correct predictions to total predictions.
    """    
    correct_predictions = sum(conf_matrix[i][i] for i in range(len(conf_matrix)))
    total_predictions = sum(sum(row) for row in conf_matrix)
    accuracy = correct_predictions / total_predictions
    return accuracy


def print_confusion_matrix(observed_codes, predicted_codes, output_file):
    """
    Prints the confusion matrix based on the actual and predicted codes.

    Parameters:
        observed_codes (list): List of actual codes.
        predicted_codes (list): List of predicted codes.

    Returns:
        None
    """
    # Extract unique codes from observed_codes
    unique_codes = sorted(set(observed_codes))
    
    # Calculate confusion matrix
    conf_matrix = confusion_matrix(observed_codes, predicted_codes)
    
    # Print headers
    header = "Actual \\ Predicted".ljust(12) + "\t".join(str(code).center(8) for code in unique_codes)
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
    
    
#Main code    
def main():
    print('Start program: PredictContinentalPopulations')
    
    # TRAINING #
    
    #Load input datafile into a DataFrame
    print('\nLoad training fileanme...')
    Training_dataset_df = pd.read_csv(Training_filename, delimiter='\t')
    
    #Normalize
    Training_dataset_df = normalize_df(Training_dataset_df.copy(), norm_threshold, Training_dataset_df)
   
    # Create an array with 50% True values followed by 50% False values
    if SPLIT_DATA:
        print('\nTraining on 50% of the data...')
        boolean_array = np.random.choice([True, False], size=len(Training_dataset_df), p=[0.5, 0.5])
        Training_dataset_df = Training_dataset_df[boolean_array]

    print('   Preparing data for RF')
    #Find the Features (X) and target (y) for Random Forest training
    X, y = prepare_rf_data(Training_dataset_df)
    y = y.values.ravel() #Flatten y to be a 1D array

    #Executing the RF model, best_model should be RandomForestRegressor()   
    best_model = execute_rf_model(X, y)
    
    print('   QC on best model = ', best_model)
    if best_model is None:
        print('main() Error: best_model is None')
        sys.exit(1)
    
    #Predict the self report continental code for the training dataset   
    df_code_pred = predict_code(Training_dataset_df.copy(), best_model, X)
   
    # Calculate the confusion matrix and accuracy for the training dataset
    #print('   Calculating the accuracy for the training data')
    #print_confusion_matrix(df_code_pred['Code'], df_code_pred['predicted_code'], output_file)


    # TESTING #
    #open(r'Output.txt', 'w').close()
    print('\nLoad testing fileanmes...')
    with open('Output.txt', "w") as output_file:

        for INPUT_TESTING_FILE_curr in INPUT_TESTING_FILE:
            print("\nNow processing file:", INPUT_TESTING_FILE_curr)
            Testing_file = INPUT_TESTING_FOLDER + '\\' + INPUT_TESTING_FILE_curr
            
            #Load input datafile into a DataFrame
            print('\nLoad testing dataset file...')
            
            #Load file
            Testing_dataset_df = pd.read_csv(Testing_file, delimiter='\t')
            
            #Zero data below thresholds, normalize columns to sum to 1, remove NaNs
            Testing_dataset_df = normalize_df(Testing_dataset_df.copy(), norm_threshold, Testing_dataset_df)

            #Removing samples already used in training
            #print("   Before removing training samples:", len(Testing_dataset_df))
            Testing_dataset_df = Testing_dataset_df[~Testing_dataset_df['SampleCode'].isin(Training_dataset_df['SampleCode'])]

            #Check that data remain
            if Testing_dataset_df.empty:
                print("main() Error: Testing_dataset_df is empty. Exiting the program.")
                sys.exit(1)
                
            #print("   After removing training samples, samples remaining:", len(Testing_dataset_df))

            print('   Preparing data for RF')
            X_pred, Y_pred = prepare_rf_data(Testing_dataset_df)
        
            #Predict self reported continental code in testing dataset
            df_code_pred = predict_code(Testing_dataset_df.copy(), best_model, X_pred)
        
            # Calculate the confusion matrix and accuracy for the testing dataset
            print('   Calculating the accuracy for the testing data')
            print_confusion_matrix(df_code_pred['Code'], df_code_pred['predicted_code'], output_file)
   
    # print('Save results to a csv file')
    #df_code_pred.to_csv('d:\Output.csv', index=False)  # You can change 'output.csv' to your desired file name

    print('End program: PredictContinentalPopulations')

if __name__ == '__main__':
    main()
    