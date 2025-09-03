import math

def calculate_plume(yield_kt, wind_speed_kph, wind_direction):
    """
    Calculates simplified fallout plume dimensions and orientation based on a WSEG-10-like model.
    Yield and wind speed are the key factors.
    """
    # A simplified empirical model:
    # Plume length is proportional to yield and wind speed.
    plume_length_km = 1.5 * (yield_kt ** 0.5) * (wind_speed_kph ** 0.8)
    # Plume width is a fraction of its length.
    plume_width_km = plume_length_km / 4

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