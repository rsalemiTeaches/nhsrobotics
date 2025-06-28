# This function takes the 5 raw sensor readings, finds the single
# closest valid reading (ignoring zeros), and returns it.
def get_closest_distance(d_l, d_cl, d_c, d_cr, d_r):
    # Put all readings into a list.
    all_readings = [d_l, d_cl, d_c, d_cr, d_r]
    
    # Use a list comprehension to create a new list containing only valid readings (> 0).
    # This is a more concise and efficient way to write the filter.
    valid_readings = [d for d in all_readings if d > 0]

    # If there are no valid readings, return a large number.
    if not valid_readings:
        return 999
    
    # If there are valid readings, return the smallest one.
    return min(valid_readings)

