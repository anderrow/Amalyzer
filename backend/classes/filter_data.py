from datetime import datetime, timedelta
import pandas as pd

class FilterData:
    """
    Given a pandas DataFrame, this base class allows filtering logic to be applied
    in subclasses using the apply_filter() method.
    """
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def apply_filter(self):
        raise NotImplementedError(
            f"Subclasses should implement this method. Call one of: {[cls.__name__ for cls in FilterData.__subclasses__()]}"
        )


class FilterByString(FilterData):
    """
    Filters the DataFrame by checking if the specified value (case-insensitive, trimmed)
    exists within the specified column (which should contain strings).
    """
    def __init__(self, data: pd.DataFrame, value: str, column: str):
        super().__init__(data)
        self.value = value.strip().lower()
        self.column = column

    def apply_filter(self) -> pd.DataFrame:
        if self.column not in self.data.columns:
            raise ValueError(f"Column '{self.column}' not found in DataFrame.")

        # Ensure the column is treated as string, fill NaNs to avoid errors
        column_series = self.data[self.column].fillna("").astype(str)

        # Filter rows where the normalized value is contained in the column (case-insensitive)
        filtered_df = self.data[column_series.str.lower().str.contains(self.value)].copy() # copy() is saffer  

        return filtered_df


class FilterByDateTime(FilterData):
    """
    Filters the DataFrame by checking if the datetime in the specified column is
    greater or equal than the threshold calculated as current time minus the specified timedelta.
    """
    def __init__(self, data: pd.DataFrame, value: int, timeUnit: str, column: str):
        super().__init__(data)
        self.value = value
        self.timeUnit = timeUnit.lower()  # e.g. 'minutes', 'hours', 'days'
        self.column = column

    def apply_filter(self) -> pd.DataFrame:
        if self.column not in self.data.columns:
            raise ValueError(f"Column '{self.column}' not found in DataFrame.")

        threshold_time = datetime.now() - timedelta(**{self.timeUnit: self.value})

        # Convert column to datetime (if not already) and coerce errors to NaT
        col_dt = pd.to_datetime(self.data[self.column], errors='coerce')

        # Filter rows where datetime >= threshold_time
        filtered_df = self.data[col_dt >= threshold_time].copy() #Copy() makes everything saffer

        return filtered_df
