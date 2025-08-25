# This is intended to be used for the API of the LED control system so that it is easier to use for end users
# TODO: Implement API endpoints for LED control
def convert_zigzag_wiring_to_matrix(led_num):
    """
    Takes a single LED number and converts it to a zigzag matrix position.
    Returns a tuple (row, col) representing the position in the matrix.
    """
    row = led_num // 7
    col = led_num % 7
    return (row, col)

assert convert_zigzag_wiring_to_matrix(27) == (3, 6)
assert convert_zigzag_wiring_to_matrix(7) == (1, 0)