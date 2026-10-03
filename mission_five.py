################################################################################
# mission_five.py
#
# Description:
# [Describe What your mission does here]
#
# Author(s): [Your Name(s)]
# Date: [YYYY-MM-DD]
# Version: 1.0
#
# Dependencies:
# - robot
# - pybricks.tools
#
################################################################################
from robot import robot
from pybricks.tools import wait, StopWatch

# Crane settings: tune these on the robot.
# If the crane goes down when it should go up, flip the sign of CRANE_LIFT_ANGLE.
CRANE_SPEED = 170  # deg/sec of the crane motor
CRANE_LIFT_ANGLE = 90  # motor degrees between "down" and "up"


def crane_up(r: robot):
    r.lam.run_angle(CRANE_SPEED, CRANE_LIFT_ANGLE)


def crane_down(r: robot):
    r.lam.run_angle(CRANE_SPEED, -CRANE_LIFT_ANGLE)


def mission_five(r: robot):
    print("Running Mission 5")
    # Start with the crane DOWN; that position counts as 0.
    r.lam.reset_angle(0)

    r.robot.straight(200)
    print("Running Crane 5")
    crane_down(r)
    crane_up(r)
    #r.robot.straight(200)
    #crane_down(r)
################################
# KEEP THIS AT THE END OF THE FILE
# This redirects to running main.
################################
if __name__ == "__main__":
    from main import main
    main()
