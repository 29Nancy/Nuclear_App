def calculate_initial_dose_rate(yield_kt):
    """
    Calculates a representative initial dose rate at t=1 hour for a location near the blast.
    This is a simplified model to ensure the graph responds to yield changes.
    """
    # A simplified constant for a nominal blast location.
    # The initial dose rate scales with the yield.
    # A real model would be far more complex, considering distance and wind.
    
    # Base rate for 1 kt yield at a close-in location
    base_rate = 100 
    
    initial_dose_rate = base_rate * (yield_kt / 15)  # Scale relative to 15 kt
    
    return initial_dose_rate