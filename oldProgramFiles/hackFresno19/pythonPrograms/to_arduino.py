from pythonPrograms.computer_vision import ComputerVision


# This will be a bool returned from the arduino ensuring sensors are clear.
# These bools may not be necessary.
# The safety measures put in place should be coded into the arduino.
# The arduino will have faster, more reliable readings and ability to stop
# the robot.
# sensors_clear = True  # Also inform the operator that it is halted when False.
# operator_starts = True  # True when the operator has "unlocked" the robot. Ready for use.


def guide_steering():
    """Get information about hose location, make steering decisions."""
    # Create an instance of ComputerVision using camera 0 (web/rpi cam).
    c_v = ComputerVision(0)
    line_pos = c_v.find_line()

    if line_pos == "R":  # Right
        # Send signal to go right because the line is too far right.
        pass

    if line_pos == "L":  # Left
        # Send signal to go left because the line is too far left.
        pass

    if line_pos == "C":  # Continue:
        # Send signal to keep going forwards.
        pass
