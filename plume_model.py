# plume_model.py

def calculate_plume(yield_mt, wind_speed_kph):
    """
    Calculates simplified fallout plume dimensions.
    Assumes an elliptical shape.
    """
    # These are simplified rules of thumb.
    # A more complex model would require detailed physics equations.
    plume_length_km = 10 * yield_mt * (wind_speed_kph / 10)
    plume_width_km = plume_length_km / 3

    return {
        'length': plume_length_km,
        'width': plume_width_km
    }

# You can test this function here to make sure it works.
# For a 15 MT blast with 20 km/h winds:
# dimensions = calculate_plume(15, 20)
# print(f"Plume Length: {dimensions['length']} km")
# print(f"Plume Width: {dimensions['width']} km")