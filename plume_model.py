# plume_model.py

import numpy as np

# A dictionary to map wind direction strings to rotation angles in degrees.
DIRECTION_MAP = {
    'N': 0, 'NE': 45, 'E': 90, 'SE': 135,
    'S': 180, 'SW': 225, 'W': 270, 'NW': 315
}

def _calculate_centerline_dose(yield_kt, wind_speed_mph, fission_fraction=0.5):
    """
    Calculates the H+1 dose rate (rad/hr) along the downwind centerline using the WSEG-10 model.
    This is the core physics engine based on Glasstone & Dolan's "The Effects of Nuclear Weapons".
    """
    # --- Constants and Unit Conversions ---
    R1 = 2900  # Unit-time reference dose rate: (rad/hr)/(kt/mi^2)
    Y_MT = yield_kt / 1000.0  # The formula requires weapon yield in MEGATONS.

    # --- Generate distances to calculate for ---
    # We create an array of 300 points from 0.1 miles to 300 miles downwind.
    distances_miles = np.linspace(0.1, 300, num=300)
    
    # --- W(d) Calculation: Total Activity Deposited per Unit Area ---
    # This is the main empirical formula from the WSEG-10 report.
    numerator = 6.3 * (Y_MT**0.18) * np.exp(-0.61 * ((wind_speed_mph / 15.0)**-0.4) * (distances_miles**0.75))
    denominator = wind_speed_mph * (distances_miles**1.9)
    Wd = numerator / denominator

    # --- Final Dose Rate Calculation ---
    # The H+1 dose rate is a product of the reference rate, the deposited activity, and the fission fraction.
    dose_rates_rad_hr = R1 * Wd * fission_fraction

    # --- Format the Output ---
    # Return a clean list of (distance, dose_rate) tuples, filtering out negligible values.
    centerline_data = [(d, r) for d, r in zip(distances_miles, dose_rates_rad_hr) if r > 0.1]
    
    return centerline_data

def _generate_contours(centerline_data, target_doses=[1000, 300, 100, 30, 10]):
    """
    Takes centerline data and generates contour polygons for specific dose rates.
    It uses a Gaussian crosswind distribution model to determine the plume's width.
    """
    contours = {}
    k = 2.77  # An empirical constant for atmospheric stability.

    for dose_level in target_doses:
        # Find all points on the centerline where the dose is higher than our target level.
        relevant_points = [(d, r) for d, r in centerline_data if r >= dose_level]

        # If no part of the plume reaches this dose level, skip it.
        if not relevant_points:
            continue

        upper_edge = []
        for distance, centerline_dose in relevant_points:
            # This is the formula to calculate the crosswind distance 'y' for the target dose level.
            ratio = dose_level / centerline_dose
            log_ratio = np.log(ratio)
            crosswind_distance = distance * np.sqrt(-(1 / k) * log_ratio)
            
            # Add the calculated point (x=distance, y=crosswind_distance) for the upper edge of the plume.
            upper_edge.append((distance, crosswind_distance))

        # The lower edge is a mirror image of the upper edge across the x-axis.
        lower_edge = [(d, -y) for d, y in reversed(upper_edge)]

        # Combine the upper and lower edges with the ground zero point (0,0) to form a closed polygon.
        polygon_points = [(0, 0)] + upper_edge + lower_edge
        contours[f'{dose_level}_rad_hr'] = polygon_points
    
    return contours

def calculate_full_plume(yield_kt, wind_speed_kph, wind_direction, fission_fraction=0.5):
    """
    This is the main public function that your Kivy app will call.
    It orchestrates the entire calculation process.
    """
    # --- Step 1: Unit Conversions ---
    # The WSEG-10 model requires units of miles per hour.
    wind_speed_mph = wind_speed_kph * 0.621371

    # --- Step 2: Core Physics Calculation ---
    # Calculate the dose rates along the downwind centerline.
    centerline_data = _calculate_centerline_dose(yield_kt, wind_speed_mph, fission_fraction)
    
    # --- Step 3: Contour Generation ---
    # Generate the drawable polygons from the centerline data.
    contour_polygons = _generate_contours(centerline_data)

    # --- Step 4: Final Output ---
    # Package everything into a dictionary that's easy for the UI to use.
    angle = DIRECTION_MAP.get(wind_direction.upper(), 0)
    
    output = {
        'angle': angle,
        'contours': contour_polygons,
        'centerline_data': centerline_data # Include raw data for potential graphs or analysis
    }
    
    return output

# This block allows you to test the model independently by running "python plume_model.py"
if __name__ == '__main__':
    # --- Test Inputs ---
    test_yield = 100  # 100 kilotons
    test_wind_kph = 24  # approx 15 mph
    test_direction = 'E' # Plume will go East

    # --- Run the calculation ---
    plume_data = calculate_full_plume(test_yield, test_wind_kph, test_direction)

    # --- Print the results for verification ---
    print(f"--- Fallout Plume Simulation ---")
    print(f"Yield: {test_yield} kt, Wind: {test_wind_kph} kph, Direction: {test_direction}\n")
    print(f"Calculated Plume Angle: {plume_data['angle']} degrees\n")

    print("Contour Data:")
    for dose_level, points in plume_data['contours'].items():
        # Find the maximum length (max x-value) for each contour
        max_length = max(p[0] for p in points)
        print(f"  - {dose_level}: {len(points)} points, max downwind distance: {max_length:.2f} miles")