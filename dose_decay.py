import math

def generate_dose_data(initial_dose_rate):
    """
    Generates dose data points for a graph based on a dynamic initial dose rate.
    """
    # Using the t^-1.2 rule, a standard model for fallout decay
    time_points = [x for x in range(1, 101)]
    dose_data = [initial_dose_rate * (time ** -1.2) for time in time_points]
    
    return time_points, dose_data