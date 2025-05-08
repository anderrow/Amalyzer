import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
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
    Given two columns (datetime type), the subclass returns a data dictionary
    containing the delta of this two columns, with the option of overwriting the
    second column with the result (default mode = overwrite). 
    """
    def __init__(self, data, column1, column2, overwrite = True, new_column_name = "duration"):
        super().__init__(data)
        self.column1 = column1
        self.column2 = column2
        self.overwrite = overwrite
        self.new_colum_name = new_column_name
    
    def apply_calculation(self):
        # Initialize an empty list to store new results
        filtered_data = []  

        for row in self.data:
            #Check if they are datetime objects
            if isinstance(row[self.column1], datetime) and isinstance(row[self.column2], datetime):
                #Calculate delta and save it in seconds
                delta = round((row[self.column2] - row[self.column1]).total_seconds(), 1) #max 1 float
                #Caclulate in minutes if delta is bigger than 60 seconds
                if delta > 60:
                    minutes = int(delta//60)   #Integrer minutes
                    seconds = int(delta % 60)  # Rest of seconds
                    # Format seconds to always show two digits (e.g., 03 instead of 3)
                    if seconds<10:
                        delta=f"{minutes}:0{seconds}"
                    else:
                        delta=f"{minutes}:{seconds}"
                else:
                    delta=f"{delta}" #Convert to str (keep all the data in the column with the same data type)

                #Is overwrite is requested overwrite, otherwise, write it down in new column which is named duration
                if self.overwrite:
                    row[self.column2] = delta
                else:
                    row[self.new_column_name] = delta

                filtered_data.append(row)
        return filtered_data
    
class CaclulatPercent(Calculation):
    """
    Given a value (float or int) and the percentage to be calculated, the subclass returns a 
    data dictionary containing the result of the percentage calculation. By default, the result 
    overwrites the percentage column, but this behavior can be changed.
    (result  = value × percentage ÷ 100)
    """
    def __init__(self, data, value, percentage, overwrite = True, new_column_name="calc_per"):
        super().__init__(data)
        self.value = value
        self.percentage = percentage
        self.overwrite = overwrite
        self.new_column_name = new_column_name
    
    def apply_calculation(self):
        # Initialize an empty list to store new results
        filtered_data = []  

        for row in self.data:
            if isinstance(row[self.value], float) and isinstance(row[self.percentage],  float):
                result =  round((row[self.value]*row[self.percentage]/100), 2)
                #Is overwrite is requested overwrite, otherwise, write it down in new column which is named duration
                if self.overwrite:
                    row[self.percentage] = result
                else:
                    row[self.new_column_name] = result

                filtered_data.append(row)
        return filtered_data
    
class IsInTolerance(Calculation):
    """
    Given a requested value (float or int), a real value (float or int), and a tolerance percentage, the 
    subclass returns a data dictionary containing a new column named "Deviation" (default) with three possible results:
    1 = Over Tolerance
    2 = Within Tolerance
    3 = Under Tolerance
    """
    def __init__(self, data, requested, real, tolerance, new_column_name="Deviation"):
        super().__init__(data)
        self.requested=requested
        self.real=real
        self.tolerance = tolerance
        self.new_column_name = new_column_name
    
    def apply_calculation(self):
        # Initialize an empty list to store new results
        filtered_data = []

        for row in self.data:
            if (isinstance(row[self.requested],(int, float)) 
                and isinstance(row[self.tolerance],  (int, float)) 
                and isinstance(row[self.real],(int, float)) ):
                #Calculate Upper and Lower tolerance in "real" number instead of percentage
                Tol_bass_1 = row[self.tolerance]/100
                UpperTol = row[self.requested] *(1+Tol_bass_1)
                LowerTol = row[self.requested] *(1-Tol_bass_1)

                #Clasify by Over, Under and Within tolerance
                if row[self.real] < UpperTol:
                    row[self.new_column_name] = 1 #Over Tolerance
                elif row[self.real] > LowerTol: 
                    row[self.new_column_name] = 3 #Under Tolerance
                else:
                    row[self.new_column_name] = 2 #Within tolerance
                
                #Save the data
                filtered_data.append(row)
        
        return filtered_data

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
        
