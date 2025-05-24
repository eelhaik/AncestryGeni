import logging
from typing import List, Optional, Tuple, Callable
import pandas as pd
from sklearn.pipeline import Pipeline


def configure_logging():
    try:
        import logger_config  # A separate module for centralized logging
        return logging.getLogger(__name__).getChild('DataPreprocessor')  # This logger is now a child of the root logger
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('DataPreprocessor')
        logger.info("Using basic logging as logger_config is not available.")
        return logger


logger = configure_logging()
PREPROCESS_PIPELINE_STEPS = []


class InvalidDataFrameError(Exception):
    """Custom exception for invalid DataFrame."""

    def __init__(self, message: str):
        super().__init__(f"Invalid DataFrame: {message}")


class DataPreprocessor:
    """
    A class for preprocessing data using a pipeline.
    """

    def __init__(self, df: pd.DataFrame, columns_of_interest: Optional[List[str]] = None,
                 pipeline_steps: Optional[List[Tuple[str, Callable]]] = None) -> None:
        self.setup_attributes(df, columns_of_interest, pipeline_steps)

    def setup_attributes(self, df, columns_of_interest, pipeline_steps):
        """
        Setup class attributes.

        :param df: DataFrame containing the data.
        :param columns_of_interest: List of columns to focus on.
        :param pipeline_steps: List of pipeline steps.
        """
        self.df = self.validate_data(df, columns_of_interest)
        self.columns_of_interest = columns_of_interest
        self.pipeline_steps = pipeline_steps or PREPROCESS_PIPELINE_STEPS
        self.is_processed = False

    @staticmethod
    def validate_data(df: pd.DataFrame, columns_of_interest: Optional[List[str]]) -> pd.DataFrame:
        if df is None or df.empty:
            raise InvalidDataFrameError("DataFrame should not be None or empty.")
        if not isinstance(df, pd.DataFrame):
            raise InvalidDataFrameError("Expected a DataFrame object.")
        if columns_of_interest and not all(column in df.columns for column in columns_of_interest):
            raise InvalidDataFrameError("DataFrame missing one or more required columns.")
        return df.copy()

    def apply_pipeline(self) -> pd.DataFrame:
        try:
            if self.columns_of_interest:
                self.df = self.df[self.columns_of_interest]

            if self.pipeline_steps:
                pipeline = Pipeline(steps=self.pipeline_steps)
                self.df = pd.DataFrame(pipeline.fit_transform(self.df), columns=self.df.columns)

            self.is_processed = True
            logger.info("Data preprocessing completed.")
            return self.df

        except Exception as e:
            logger.error(f"An error occurred during data preprocessing: {e}")
            raise e

    @property
    def processed(self) -> bool:
        return self.is_processed

    def get_data(self) -> pd.DataFrame:
        if self.is_processed:
            return self.df.copy()
        else:
            raise ValueError("Data has not been processed yet.")
