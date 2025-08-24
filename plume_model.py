import math

def calculate_plume(yield_mt, wind_speed_kph, wind_direction):
    """
    Calculates simplified fallout plume dimensions and orientation.
    """
    # Simplified physics model for plume dimensions
    plume_length_km = 10 * yield_mt * (wind_speed_kph / 10)
    plume_width_km = plume_length_km / 3

    # Convert direction (e.g., 'NE') to an angle in degrees for rotation
    direction_map = {
        'N': 0, 'NE': 45, 'E': 90, 'SE': 135,
        'S': 180, 'SW': 225, 'W': 270, 'NW': 315
    }
    angle = direction_map.get(wind_direction.upper(), 0)

    return {
        'length': plume_length_km,
        'width': plume_width_km,
        'angle': angle
    }