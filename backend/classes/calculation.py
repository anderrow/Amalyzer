from datetime import datetime, timedelta

class Calculation:
    """
    Given a data dictionary with the format List[Dict[str, Any]], the class returns
    a data dictionary containing the results of the requested filter in the subclass.
    """
    def __init__(self, data):
        self.data = data

    def apply_calculation(self):
        raise NotImplementedError("Subclasses should implement this method.")

class CalculateDate(Calculation):
    """
    Given two columns (datetime type), the subclass returns a data dictionary
    containing the delta of this two columns, with the option of overwriting the
    second column with the result (Is doing it by default). 
    """
    def __init__(self, data, column1, column2, overwrite = True):
        super().__init__(data)
        self.column1 = column1
        self.column2 = column2
        self.overwrite = overwrite
    
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
                    if delta<10:
                        delta=f"{minutes}:0{seconds}"
                    else:
                        delta=f"{minutes}:{seconds}"
                else:
                    delta=f"{delta}" #Convert to str (keep all the data in the column with the same data type)

                #Is overwrite is requested overwrite, otherwise, write it down in new column which is named duration
                if self.overwrite:
                    row[self.column2] = delta
                else:
                    row["duration"] = delta

                filtered_data.append(row)
        return filtered_data