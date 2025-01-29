from typing import Callable, Dict, Any, Optional
import numpy as np
import logging
from sklearn.model_selection import KFold, RandomizedSearchCV

# Constants
DEFAULT_CV_FOLDS = 5
DEFAULT_N_RANDOM_ITER = 10
DEFAULT_SCORING_METRICS = 'r2'

logger = logging.getLogger(__name__)


class InvalidParameterError(Exception):
    """Exception raised for invalid parameters."""
    pass


class Regressors:
    """Class to handle various regression models and their training.

    Attributes:
        model_dict (dict): Dictionary of models and their details.
        default_cv_folds (int): Default number of CV folds.
        default_n_random_iter (int): Default number of random iterations.
    """

    def __init__(self, model_dict: Optional[Dict[str, Any]] = None,
                 default_cv_folds: int = DEFAULT_CV_FOLDS,
                 default_n_random_iter: int = DEFAULT_N_RANDOM_ITER) -> None:
        """Initialize the Regressors class."""
        logger.info("Initializing the Regressors class.")
        self.model_dict = model_dict or {}
        self.default_cv_folds = default_cv_folds
        self.default_n_random_iter = default_n_random_iter

    def add_model(self, model_name, model_class, supports_multi_output=False, hyperparameters=None):
        if hyperparameters is None:
            hyperparameters = {}
        self.model_dict[model_name] = {
            'model': model_class,
            'supports_multi_output': supports_multi_output,
            'hyperparameters': hyperparameters  # Accept and store the hyperparameters here
        }
    def train_model(self, model_type: str, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> Optional[Any]:
        """Train the model of the given type with the provided training data."""
        try:
            logger.info(f"Starting model training for {model_type}.")
            return self._train_model_internal(model_type, X_train, y_train, **kwargs)
        except InvalidParameterError as e:
            logger.error(f"InvalidParameterError: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in train_model: {e}")
            return None

    def _train_model_internal(self, model_type: str, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> Any:
        """Internal method to validate and train models."""
        try:
            self._validate_params(model_type, X_train, y_train)
            cv_folds = kwargs.get('cv_folds', self.default_cv_folds)
            model = self._create_model(model_type)
            logger.info(f"Performing K-Fold Cross-Validation with {cv_folds} folds.")
            kfold = KFold(n_splits=cv_folds, shuffle=True, random_state=kwargs.get('random_state'))
            return self._train_or_tune_model(model, X_train, y_train, kfold, **kwargs)
        except Exception as e:
            logger.error(f"Error in _train_model_internal: {e}")
            raise

    def _validate_params(self, model_type: str, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Validate the model type and training data."""
        if model_type not in self.model_dict:
            raise InvalidParameterError(f"Invalid model type: {model_type}")
        if X_train.shape[0] != y_train.shape[0]:
            raise InvalidParameterError("Mismatch between number of samples in X_train and y_train.")

    def _create_model(self, model_type: str) -> Any:
        """Create a model instance based on the given type."""
        return self.model_dict[model_type]['model_class']()

    def _train_or_tune_model(self, model: Any, X_train: np.ndarray, y_train: np.ndarray, kfold: KFold, **kwargs) -> Any:
        """Train or tune the model based on whether a hyperparameter grid is provided."""
        param_grid = kwargs.get('param_grid')
        if param_grid:
            logger.info("Hyperparameter grid provided. Starting hyperparameter tuning.")
            return self._perform_hyperparameter_tuning(model, param_grid, X_train, y_train, kfold, **kwargs)
        logger.info("No hyperparameter grid provided. Training model with default parameters.")
        model.fit(X_train, y_train)
        return model

    def _perform_hyperparameter_tuning(self, model: Any, param_grid: Dict[str, Any], X_train: np.ndarray,
                                       y_train: np.ndarray, kfold: KFold, **kwargs) -> Any:
        """Perform hyperparameter tuning using RandomizedSearchCV."""
        n_random_iter = kwargs.get('n_random_iter', self.default_n_random_iter)
        scoring_metrics = kwargs.get('scoring_metrics', DEFAULT_SCORING_METRICS)
        random_search = RandomizedSearchCV(
            model, param_distributions=param_grid, n_iter=n_random_iter,
            scoring=scoring_metrics, cv=kfold, verbose=2, n_jobs=-1,
            refit=kwargs.get('refit_metric', DEFAULT_SCORING_METRICS)
        )
        random_search.fit(X_train, y_train)
        logger.info(
            f"Hyperparameter tuning completed. Best Params: {random_search.best_params_}, Best Score: {random_search.best_score_}")
        return random_search.best_estimator_
