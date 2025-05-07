from datetime import datetime, timedelta

class FilterData:
    """
    Given a data dictionary with the format List[Dict[str, Any]],the class returns
    a data dictionary containing the results of the requested filter in the subclass.
    """
    def __init__(self, data):
        self.data = data

    def apply_filter(self):
        raise NotImplementedError(f"Subclasses should implement this method. Call one of: {[cls.__name__ for cls in FilterData.__subclasses__()]}")


class FilterByString(FilterData):
    """
    Given a value to filter in a column, the subclass returns a data dictionary
    containing the rows that match the specified value in the column. 
    """
    def __init__(self, data, value, column):
        super().__init__(data)
        self.value = value
        self.column = column

    def apply_filter(self):
        # Normalize the value value (strip spaces and convert to lowercase)
        normalized_value = self.value.strip().lower()

        filtered_data = []  # Initialize an empty list to store filtered results

        # Iterate over the data and apply the filter condition
        for row in self.data:
            # Check if column is a string and if it contains the normalized value
            if isinstance(row[self.column], str) and normalized_value in row[self.column].strip().lower():
                filtered_data.append(row)  # If the condition is met, add the row to the list

        return filtered_data  # Return the filtered data


class FilterByDateTime(FilterData):
    """
    Given a value, a time unit (Minutes, Hours, or Days), and a column with DateTime type,
    the subclass returns a data dictionary containing the rows in which the column date satisfies
    the condition: (CurrentTime) - (Time specified by time unit and value) ≤ column.
    """
    def __init__(self, data, value, timeUnit, column):
        super().__init__(data)
        self.value = value
        self.timeUnit = timeUnit.lower() #'minutes', 'hours' or 'days'. Requested key for datetime library
        self.column = column

    def apply_filter(self):
        # Calculate the threshold time (current time minus the specified number of minutes)
        threshold_time = datetime.now() - timedelta(**{self.timeUnit: self.value})

        filtered_data = []  # Initialize an empty list to store filtered results

        # Iterate over the data and apply the filter condition
        for row in self.data:
            # Check if column is a datetime object and if it is greater than or equal to threshold_time
            if isinstance(row[self.column], datetime) and row[self.column] >= threshold_time:
                filtered_data.append(row)  # If the condition is met, add the row to the list

        return filtered_data  # Return the filtered data
