# dose_decay.py
import math

def generate_dose_data(initial_dose_rate):
    """
    Generates dose data points for a graph showing radioactive decay over time.
    
    This follows the t^-1.2 decay law for nuclear fallout radiation,
    which is a well-established empirical relationship.
    
    Args:
        initial_dose_rate (float): Initial dose rate in rad/hr at t=1 hour
    
    Returns:
        tuple: (time_points, dose_data) where both are lists of equal length
    """
    # Using the t^-1.2 rule, a standard model for fallout decay
    time_points = [x for x in range(1, 101)]  # 1 to 100 hours
    dose_data = [initial_dose_rate * (time ** -1.2) for time in time_points]
    
    return time_points, dose_data

def calculate_integrated_dose(initial_dose_rate, start_time, end_time):
    """
    Calculates the total integrated dose over a time period.
    
    Args:
        initial_dose_rate (float): Initial dose rate in rad/hr at t=1 hour
        start_time (float): Start time in hours
        end_time (float): End time in hours
    
    Returns:
        float: Total integrated dose in rads
    """
    # For the t^-1.2 decay law, the integral is:
    # ∫ R₀ * t^-1.2 dt = R₀ * (t^-0.2) / (-0.2) = -5 * R₀ * t^-0.2
    
    def antiderivative(t):
        return -5 * initial_dose_rate * (t ** -0.2)
    
    return antiderivative(end_time) - antiderivative(start_time)

# Test function - run this file directly to see sample output
if __name__ == '__main__':
    print("Testing dose decay calculations...")
    
    # Test the basic dose data generation
    time_points, dose_data = generate_dose_data(1000)
    
    print(f"Initial dose rate: {dose_data[0]:.1f} rad/hr")
    print(f"Dose rate after 24 hours: {dose_data[23]:.1f} rad/hr")
    print(f"Dose rate after 48 hours: {dose_data[47]:.1f} rad/hr")
    print(f"Dose rate after 72 hours: {dose_data[71]:.1f} rad/hr")
    
    # Test integrated dose calculation
    integrated_24h = calculate_integrated_dose(1000, 1, 25)  # First 24 hours
    print(f"\nTotal dose in first 24 hours: {integrated_24h:.1f} rads")
    
    integrated_week = calculate_integrated_dose(1000, 1, 169)  # First week
    print(f"Total dose in first week: {integrated_week:.1f} rads")