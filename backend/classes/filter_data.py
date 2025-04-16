from datetime import datetime, timedelta

class FilterData:
    """
    Given a data dictionary with the format List[Dict[str, Any]],the class returns
    a data dictionary containing the results of the requested filter in the subclass.
    """
    def __init__(self, data):
        self.data = data

    def apply_filter(self):
        raise NotImplementedError("Subclasses should implement this method.")


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
    def __init__(self, data, minutes_ago):
        super().__init__(data)
        self.minutes_ago = minutes_ago

class FilterByDateTime(FilterData):
    def __init__(self, data, minutes_ago):
        super().__init__(data)  # Call the parent constructor to initialize data
        self.minutes_ago = minutes_ago  # Store the number of minutes for filtering

    def apply_filter(self):
        # Calculate the threshold time (current time minus the specified number of minutes)
        threshold_time = datetime.now() - timedelta(minutes=self.minutes_ago)

        filtered_data = []  # Initialize an empty list to store filtered results

        # Iterate over the data and apply the filter condition
        for row in self.data:
            # Check if 'StartTime' is a datetime object and if it is greater than or equal to threshold_time
            if isinstance(row['StartTime'], datetime) and row['StartTime'] >= threshold_time:
                filtered_data.append(row)  # If the condition is met, add the row to the list

        return filtered_data  # Return the filtered data
