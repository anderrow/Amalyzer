import pandas as pd
import numpy as np
from datetime import datetime

from backend.classes.graphs import TraceData

class Calculation:
    """
    Given a data dictionary with the format List[Dict[str, Any]], the class returns
    a data dictionary containing the results of the requested filter in the subclass.
    """
    def __init__(self, data):
        self.data = data

    def apply_calculation(self):
        raise NotImplementedError(f"Subclasses should implement this method. Call one of: {[cls.__name__ for cls in Calculation.__subclasses__()]}")

class CaclulateDateDelta(Calculation):
    """
    Calculates the delta between two datetime columns in seconds, and formats it.
    If `overwrite=True`, replaces column2 with the formatted duration.
    Else, creates a new column with name `new_column_name`.
    """
    def __init__(self, data: pd.DataFrame, column1: str, column2: str, overwrite=True, new_column_name="duration"):
        super().__init__(data)
        self.column1 = column1
        self.column2 = column2
        self.overwrite = overwrite
        self.new_column_name = new_column_name

    def apply_calculation(self) -> pd.DataFrame:
        # Ensure columns are datetime
        self.data[self.column1] = pd.to_datetime(self.data[self.column1], errors="coerce")
        self.data[self.column2] = pd.to_datetime(self.data[self.column2], errors="coerce")

        # Compute delta in seconds
        delta_seconds = (self.data[self.column2] - self.data[self.column1]).dt.total_seconds()

        # Format the delta
        def format_delta(seconds):
            if pd.isna(seconds):
                return None
            seconds = round(seconds, 1)
            if seconds > 60:
                minutes = int(seconds // 60)
                sec = int(seconds % 60)
                return f"{minutes}:{sec:02d} min"
            else:
                return f"{seconds:.1f} s"

        formatted = delta_seconds.apply(format_delta)

        if self.overwrite:
            self.data[self.column2] = formatted
        else:
            self.data[self.new_column_name] = formatted

        return self.data
    
class CaclulatPercent(Calculation):
    """
    Given two numeric columns (value and percentage), calculates:
        result = value × percentage ÷ 100
    Overwrites the percentage column or stores the result in a new column.
    """
    def __init__(self, data: pd.DataFrame, value: str, percentage: str, overwrite=True, new_column_name="calc_per"):
        super().__init__(data)
        self.value = value
        self.percentage = percentage
        self.overwrite = overwrite
        self.new_column_name = new_column_name

    def apply_calculation(self) -> pd.DataFrame:
        # Ensure numeric values (NaNs remain if conversion fails)
        self.data[self.value] = pd.to_numeric(self.data[self.value], errors="coerce")
        self.data[self.percentage] = pd.to_numeric(self.data[self.percentage], errors="coerce")

        # Compute percentage
        result = (self.data[self.value] * self.data[self.percentage] / 100).round(2)

        if self.overwrite:
            self.data[self.percentage] = result
        else:
            self.data[self.new_column_name] = result

        return self.data
    
class IsInTolerance(Calculation):
    """
    Given requested, actual, and tolerance (%) columns, this class adds a new column (default: 'Deviation') 
    with:
        1 = Over Tolerance
        2 = Within Tolerance
        3 = Under Tolerance
    """
    def __init__(self, data: pd.DataFrame, requested: str, real: str, tolerance: str, new_column_name="Deviation"):
        super().__init__(data)
        self.requested = requested
        self.real = real
        self.tolerance = tolerance
        self.new_column_name = new_column_name

    def apply_calculation(self) -> pd.DataFrame:
        # Ensure numeric columns
        self.data[self.requested] = pd.to_numeric(self.data[self.requested], errors="coerce")
        self.data[self.real] = pd.to_numeric(self.data[self.real], errors="coerce")
        self.data[self.tolerance] = pd.to_numeric(self.data[self.tolerance], errors="coerce")

        # Calculate tolerance bounds
        tol_fraction = self.data[self.tolerance] / 100
        upper_tol = self.data[self.requested] * (1 + tol_fraction)
        lower_tol = self.data[self.requested] * (1 - tol_fraction)

        # Classify deviations:
        # 1 = Over Tolerance, 3 = Under Tolerance, 2 = Within Tolerance, 4 = Requested Negative
        deviation = pd.Series(2, index=self.data.index)  # Default: Within tolerance
        deviation[self.data[self.real] > upper_tol] = 1  # Over
        deviation[self.data[self.real] < lower_tol] = 3  # Under
        deviation[self.data[self.requested] < 0] = 4  # Requested negative (Filling is requested with -1 value, with means "Fill the box")

        # Assign the result to a new column
        self.data[self.new_column_name] = deviation

        return self.data

class CalculateLogTraces(Calculation):
    
    def __init__(self, data, x_data, y_data, size, bins, grades=(1,2)):
        # Fail fast
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Expected a pandas DataFrame as input data.")
        if not isinstance(bins, int) or bins < 1:
            raise TypeError("Expected an integer value bigger than 1 for bins")
        if grades[0] < 1 or grades[1] > 10 or grades[0] > grades[1]:
            raise TypeError("Expected a tuple for grades between 1 and 10 where grades[0] < grades[1]")

        super().__init__(data)
        self.df = data
        self.x_data = x_data
        self.y_data = y_data
        self.bins = bins
        self.size = size
        self.grades = grades

    def apply_calculation(self):
        # Generate an empty list for traces
        trace_list = []

        # Intermediates (scatter plot for original data) (Raw data)
        trace_list.append(TraceData(label="Intermediates", x_data=self.df[self.x_data],  y_data=self.df[self.y_data], mode="markers", color="blue", marker=dict(size=self.df[self.size] * 3 , color='blue', opacity=0.7)))
        
        # Apply the base 10 Log
        self.df[f"log_{self.x_data}"] = np.log10(self.df[self.x_data])

        # Generate a range of values for plotting them
        x_range = np.linspace(self.df[f"log_{self.x_data}"].min(), self.df[f"log_{self.x_data}"].max(), self.bins)  # 'Bins' values evenly spaced
        
        # Polynomial regressions (this will include linear regression as grade 1)
        trace_list = self.polynomical_regressions(trace_list, x_range, self.x_data, self.y_data, self.grades)

        # Return traces
        return trace_list
    
    def polynomical_regressions(self, trace_list, x_range, x_data, y_data, grades):
        #Define colors for the different traces
        colors = ["grey", "red", "lime", "orange", "yellow", "purple", "cyan", "magenta", "brown", "darkgreen", "pink"]
        
        poly_range = 10 ** x_range

        for grade in range(self.grades[0], self.grades[1] + 1):
            coefs = np.polyfit(self.df[f'log_{x_data}'], self.df[y_data], grade)
            y_deg = np.polyval(coefs, x_range) 
            
            if grade == 1:
                trace_list.append(TraceData(label="Linear Regression", x_data=poly_range,  y_data=y_deg, mode="lines", color=colors[grade-1], dash="dash")) #1st Grade
            else:
                trace_list.append(TraceData(label=f"Polynomial Degree {grade}", x_data=poly_range,  y_data=y_deg, mode="lines", color=colors[grade-1], dash="dash")) 

        return trace_list

