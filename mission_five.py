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

def mission_five(r: robot):
    print("Running Mission 5")
    # Your code goes here...
    r.robot.straight(700)
    #r.lam.run_time(170,700)
    #r.robot.straight(200)
################################
# KEEP THIS AT THE END OF THE FILE
# This redirects to running main.
################################
if __name__ == "__main__":
    from main import main
    main()
