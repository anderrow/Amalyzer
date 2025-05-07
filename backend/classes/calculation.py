from datetime import datetime, timedelta
import pandas as pd
from sklearn.linear_model import LinearRegression

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
    
class CalculateLinearRegression(Calculation):
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

    #def apply_calculation(self):