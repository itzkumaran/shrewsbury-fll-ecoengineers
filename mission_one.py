################################################################################
# mission_one.py
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

def mission_one(r: robot):
    print("Running Mission 1")
    # Your code goes here...
    # Sample Code: Run attachment motors and drive motors
    r.robot.straight(700)
    r.robot.turn(60)
    r.robot.straight(300)
    #r.robot.straight(-95)
    #r.robot.turn(-140)
    #r.robot.straight(-110)
    #r.robot.turn(-20)
    #r.robot.straight(-120)
    #r.ram.run_time(-150,7000)
################################
# KEEP THIS AT THE END OF THE FILE
# This redirects to running main.
################################
if __name__ == "__main__":
    from main import main
    main()
