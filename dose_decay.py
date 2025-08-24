# dose_decay.py
import math

def calculate_dose_rate(initial_dose_rate, time_in_hours):
    """
    Calculates the dose rate using a simplified version of the 7-10 rule.
    """
    # Using 1 hour as the initial reference time for simplicity.
    if time_in_hours < 1:
        time_in_hours = 1  # Avoids division by zero or errors for early times

    # The -1.2 exponent is a common approximation for this rule.
    dose_rate = initial_dose_rate * (time_in_hours ** -1.2)
    return dose_rate

# You can test this function here.
# For an initial dose of 1000 rad at 1 hour:
# new_dose = calculate_dose_rate(1000, 7) # Should be around 100
# print(f"Dose rate at 7 hours: {new_dose} rad")


import math

def calculate_dose_rate(initial_dose_rate, time_in_hours):
    """
    Calculates the dose rate using a simplified version of the 7-10 rule.
    """
    if time_in_hours < 1:
        time_in_hours = 1
    dose_rate = initial_dose_rate * (time_in_hours ** -1.2)
    return dose_rate

def generate_dose_data(yield_mt, initial_dose_rate=1000):
    """
    Generates dose data points for a graph.
    """
    # Create time points from 1 to 100 hours
    time_points = [x for x in range(1, 101)]
    # Use your dose decay function to get the dose at each time point
    dose_data = [calculate_dose_rate(initial_dose_rate, time) for time in time_points]
    
    return time_points, dose_data