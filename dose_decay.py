import math

def generate_dose_data(initial_dose_rate=1000):
    """
    Generates dose data points for a graph.
    """
    time_points = [x for x in range(1, 101)]
    dose_data = [initial_dose_rate * (time ** -1.2) for time in time_points]
    
    return time_points, dose_data