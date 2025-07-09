from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any
from enum import Enum

class FilterData:
    """
    Base class for filtering a pandas DataFrame. Subclasses should implement the apply_filter() method
    to provide specific filtering logic. The data attribute holds the DataFrame to be filtered.
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
    Inherits from FilterData and implements string-based filtering logic.
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
    Inherits from FilterData and implements datetime-based filtering logic.
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

class ReadableDataFormatter:
    """
    Formats columns in a pandas DataFrame to make the data more readable and user-friendly.
    Provides methods to format specific columns such as StartTime, Actual, VMSscan, LotID,
    TypeOfDosing, Tolerance, and Deviation. The apply_all_formats() method applies all formatting.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def format_start_time(self):
        if "StartTime" in self.df.columns:
            self.df["StartTime"] = pd.to_datetime(self.df["StartTime"], errors="coerce")
            self.df["StartTime"] = self.df["StartTime"].dt.strftime("%Y-%m-%d  %H:%M") # Format to "YYYY-MM-DD HH:MM" Year-Month-Day Hour:Minute

    def format_actual(self):
        if "Actual" in self.df.columns:
            self.df["Actual"] = pd.to_numeric(self.df["Actual"], errors="coerce").round(4)

    def format_vms_scan(self):
        if "VMSscan" in self.df.columns:
            self.df["VMSscan"] = self.df["VMSscan"].map({True: "✅", False: "❌"})

    def format_type_of_dosing(self):
        if "TypeOfDosing" in self.df.columns:
            def format_dosing(val):
                try:
                    return DosingType(val).name.capitalize()
                except ValueError:
                    return f"Unknown ({val})"
            self.df["TypeOfDosing"] = self.df["TypeOfDosing"].apply(format_dosing)

    def format_tolerance(self):
        if "Tolerance" in self.df.columns and "calc_per" in self.df.columns:
            original_tolerance = self.df["Tolerance"].copy()
            original_calc_per = self.df["calc_per"].copy()
            
            def format_tolerance(row):
                try:
                    kg = float(original_calc_per[row.name]) 
                    return f"{kg:.3f} kg"
                except:
                    return original_tolerance[row.name]
            def format_percentage(row):
                try:
                    tol = float(original_tolerance[row.name])
                    return f"{tol:.2f}% "
                except:
                    return original_tolerance[row.name]
                    
            self.df["Tolerance"] = self.df.apply(format_tolerance, axis=1)
            self.df["calc_per"] = self.df.apply(format_percentage, axis=1)

    def format_deviation(self):
        if "Deviation" in self.df.columns:
            def format_deviation(val):
                try:
                    return Deviation(val).name.capitalize()
                except ValueError:
                    return f"Unknown ({val})"
            self.df["Deviation"] = self.df["Deviation"].apply(format_deviation)

    def apply_all_formats(self) -> List[Dict[str, Any]]:
        self.format_start_time()
        self.format_actual()
        self.format_vms_scan()
        self.format_type_of_dosing()
        self.format_tolerance()
        self.format_deviation()
        return self.df.to_dict(orient="records")

class DosingType(Enum):
    """
    Enum representing the type of dosing. Used for formatting and validation in data processing.
    """
    NORMAL = 1
    LEARNING = 2
    D2E = 100

class Deviation(Enum):
    """
    Enum representing the type of deviation. Used for formatting and validation in data processing.
    """
    OVERDOSING = 1
    NORMAL = 2
    UNDERDOSING = 3
    FILLER = 4