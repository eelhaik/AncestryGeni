# Standard Library Imports
import os
import json
import logging
import joblib
from datetime import datetime
from typing import Optional, List, Dict, Callable, Any, Tuple

# Third-party Imports
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator
# from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
# from sklearn.ensemble import VotingRegressor
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import train_test_split

# Constants
DEFAULT_K_SPLITS = 5
RESULTS_FOLDER = './results'

# Configure logging
def configure_logging():
    try:
        import logger_config
        return logging.getLogger(__name__).getChild('ModelExecutor')
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('ModelExecutor')
        logger.info("Using basic logging as logger_config is not available.")
        return logger

logger = configure_logging()

class ModelExecutor:
    # DEFAULT_METRICS = {'R2': r2_score, 'MSE': mean_squared_error, 'MAE': mean_absolute_error}
    # DEFAULT_KNN_NEIGHBORS = 5

    # def __init__(self, model_dict: Optional[Dict[str, Dict[str, Any]]] = None,
    #              metrics: Optional[Dict[str, Callable]] = None,
    #              transformers: Optional[List[Tuple[str, BaseEstimator]]] = None,
    #              scaler_type: Optional[str] = 'StandardScaler',
    #              use_ensemble: Optional[bool] = False,
    #              save_model: Optional[bool] = True,
    #              results_filename: Optional[str] = 'best_performance',
    #              k_splits: Optional[int] = DEFAULT_K_SPLITS,
    #              model_save_path: Optional[str] = './'):

    #     self.model_save_path = model_save_path
    #     self.setup_attributes(model_dict, metrics, transformers, scaler_type, use_ensemble, save_model,
    #                           results_filename, k_splits)
    #     self.best_models = {}

    #     # Create results folder if not exists
    #     if not os.path.exists(RESULTS_FOLDER):
    #         try:
    #             os.makedirs(RESULTS_FOLDER)
    #         except Exception as e:
    #             logger.error(f"Failed to create results folder. Error: {e}")

    # def setup_attributes(self, model_dict, metrics, transformers, scaler_type, use_ensemble, save_model, results_filename, k_splits):
    #     self.results = {}
    #     self.regressors = model_dict or {}
    #     self.validate_regressors()
    #     self.metrics = metrics or self.DEFAULT_METRICS
    #     self.validate_metrics()
    #     self.transformers = transformers or self.default_transformers()
    #     self.validate_transformers()
    #     self.scaler_type = scaler_type
    #     self.setup_scaler()
    #     self.use_ensemble = use_ensemble
    #     self.save_model = save_model
    #     self.results_filename = results_filename
    #     self.k_splits = k_splits

    #     # Add hyperparameter options
    #     self.hyperparameters = {
    #         'RandomForestRegressor': {
    #             'regressor__n_estimators': [50, 100, 200],
    #             'regressor__max_depth': [None, 10, 20, 30],
    #         },
    #         'GradientBoostingRegressor': {
    #             'regressor__n_estimators': [50, 100, 200],
    #             'regressor__learning_rate': [0.01, 0.1, 1.0],
    #         },
    #         'MLPRegressor': {
    #             'regressor__max_iter': [500, 1000],
    #             'regressor__learning_rate_init': [0.001, 0.01, 0.1],
    #             'regressor__early_stopping': [True],
    #             'regressor__solver': ['adam', 'sgd', 'lbfgs'],
    #             'regressor__alpha': [0.0001, 0.001, 0.01]
    #         },
    #         'Ridge': {
    #             'regressor__alpha': [0.1, 0.5, 1.0]
    #         },
    #         'Lasso': {
    #             'regressor__alpha': [0.1, 0.5, 1.0]
    #         }
    #     }

    # def validate_regressors(self):
    #     for method, attr in self.regressors.items():
    #         if 'model' not in attr:
    #             raise ValueError(f"Missing 'model' key for method {method} in regressors dictionary.")

    # def validate_metrics(self):
    #     for name, metric in self.metrics.items():
    #         if not callable(metric):
    #             raise ValueError(f"Metric {name} should be callable.")

    # def validate_transformers(self):
    #     for name, transformer in self.transformers:
    #         if not issubclass(type(transformer), BaseEstimator):
    #             raise ValueError(f"Transformer {name} should inherit from BaseEstimator.")

    def setup_scaler(self):
        if self.scaler_type == 'StandardScaler':
            self.transformers.append(('scaler', StandardScaler()))
        elif self.scaler_type == 'MinMaxScaler':
            self.transformers.append(('scaler', MinMaxScaler()))
        elif self.scaler_type == 'RobustScaler':
            self.transformers.append(('scaler', RobustScaler()))

    def default_transformers(self):
        return [('imputer', KNNImputer(n_neighbors=self.DEFAULT_KNN_NEIGHBORS))]

    def build_pipeline(self, cols_train):
        numeric_transformer = Pipeline(steps=self.transformers)
        return ColumnTransformer(transformers=[('num', numeric_transformer, cols_train)])

    # def execute_single_training_run(self, method, X_train, y_train, X_test, y_test, target):
    #     scores = {}
    #     try:
    #         if method not in self.regressors:
    #             logger.error(f"Method {method} not found in available regressors.")
    #             return {}

    #         if 'model' not in self.regressors[method]:
    #             logger.error(f"Model key not found for method {method}.")
    #             return {}

    #         preprocessor = self.build_pipeline(X_train.columns)
    #         pipe = Pipeline(steps=[('preprocessor', preprocessor),
    #                                ('regressor', self.regressors[method]['model']())])

    #         if method in self.hyperparameters:
    #             grid_search = GridSearchCV(pipe, self.hyperparameters[method], cv=5, scoring='r2')
    #             grid_search.fit(X_train, y_train)
    #             pipe = grid_search.best_estimator_

    #         pipe.fit(X_train, y_train)

    #         # Store the best model for each method
    #         self.best_models[method] = {'model': pipe, 'target': target}

    #         if self.save_model:
    #             model_file_name = f'best_model_{method}_{target}_{datetime.now().strftime("%Y%m%d%H%M%S")}.pkl'
    #             model_file_path = os.path.join(self.model_save_path, model_file_name)
    #             joblib.dump(pipe, model_file_path)

    #         y_pred = pipe.predict(X_test)
    #         for name, metric in self.metrics.items():
    #             scores[name] = metric(y_test, y_pred)

    #     except NotFittedError as e:
    #         logger.error(f"Model not fitted for method {method}. Error: {e}")
    #     except Exception as e:
    #         logger.error(f"Error encountered during model training: {e}")

    #     return scores

    # def execute(self, df, cols_train, cols_target=None, folder_suffix=None, selected_methods=None):
    #     if cols_target is None:
    #         cols_target = [None]

    #     for target in cols_target:
    #         X_train, X_test, y_train, y_test = self.split_data(df, cols_train, target)
    #         for method in selected_methods or self.regressors.keys():
    #             scores = self.execute_single_training_run(method, X_train, y_train, X_test, y_test, target)

    #             if method not in self.results:
    #                 self.results[method] = {}

    #             # Including multiple targets and additional details such as folder_suffix
    #             self.results[method][target] = {
    #                 'scores': scores,
    #                 'folder_suffix': folder_suffix  # A new parameter for the function
    #             }

    #     if self.use_ensemble:
    #         ensemble = VotingRegressor([(key, value['model']) for key, value in self.best_models.items()])
    #         ensemble.fit(X_train, y_train)
    #         y_pred = ensemble.predict(X_test)
    #         ensemble_scores = self.calculate_scores(y_test, y_pred)

    #         if 'Ensemble' not in self.results:
    #             self.results['Ensemble'] = {}

    #         self.results['Ensemble'][target] = {
    #             'scores': ensemble_scores,
    #             'folder_suffix': folder_suffix
    #         }

    #     # Save results as JSON
    #     results_filename_with_timestamp = f'{folder_suffix}.json'
    #     results_file_path = os.path.join(RESULTS_FOLDER, results_filename_with_timestamp)

    #     try:
    #         with open(results_file_path, 'w') as f:
    #             json.dump(self.results, f)
    #     except Exception as e:
    #         logger.error(f"Failed to save results to JSON. Error: {e}")

    # def split_data(self, df, cols_train, target):
    #     if target is None:
    #         raise ValueError("Target column cannot be None")

    #     X = df[cols_train]
    #     y = df[target]

    #     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #     return X_train, X_test, y_train, y_test

    # def calculate_scores(self, y_test, y_pred):
    #     scores = {}
    #     for name, metric in self.metrics.items():
    #         scores[name] = metric(y_test, y_pred)
    #     return scores

    # def validate(self, validation_data):
    #     pass  # Add your validation logic here



def execute(self, df, cols_train, target):
    """
    Executes preprocessing and splits the data for training and testing.

    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - cols_train (list): The list of feature columns.
    - target (str): The target column name.

    Returns:
    - Tuple: (X_train, X_test, y_train, y_test), preprocessed and split data.
    """
    # Split data
    X = df[cols_train]
    y = df[target]

    X_train, X_test, y_train, y_test = self.split_data(X, y)

    # Preprocess data
    preprocessor = self.build_pipeline(cols_train)
    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)

    return X_train, X_test, y_train, y_test

def split_data(self, X, y, test_size=0.2, random_state=42):
    """
    Splits the data into training and testing sets.

    Parameters:
    - X (pd.DataFrame): Feature data.
    - y (pd.Series): Target data.
    - test_size (float): Proportion of data to allocate to the test set.
    - random_state (int): Random seed for reproducibility.

    Returns:
    - Tuple: (X_train, X_test, y_train, y_test)
    """
    return train_test_split(X, y, test_size=test_size, random_state=random_state)
