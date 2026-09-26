################################################################################
# mission_four.py
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

def mission_four(r: robot):
    print("Running Mission 4")
    # Your code goes here...
    # Sample code: Test the speaker
    r.robot.straight(-740)
    #r.robot.drive(0,10)
    r.ram.run_time(-270,5000)
    #r.robot.stop()
################################
# KEEP THIS AT THE END OF THE FILE
# This redirects to running main.
################################
if __name__ == "__main__":
    from main import main
    main()
