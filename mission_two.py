################################################################################
# mission_two.py
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

def mission_two(r: robot):
    print("Running Mission 2")
    # Your code goes here...
    # Sample code: Test Driving in a box
    r.robot.straight(210)
    r.robot.turn(-50)
    r.robot.straight(375)
    r.robot.straight(-100)
    #r.robot.turn(70)
    #r.robot.straight(275)
    #r.robot.turn(-90)
    #r.robot.straight(470)
    #r.robot.turn(-150)
    #r.robot.straight(160)
    #r.lam.run_time(-170,480)
################################
# KEEP THIS AT THE END OF THE FILE
# This redirects to running main.
################################
if __name__ == "__main__":
    from main import main
    main()
