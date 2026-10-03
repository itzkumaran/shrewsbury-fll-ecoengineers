################################################################################
# mission_three.py
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

from robot import robot, STRAIGHT_SPEED, TURN_RATE
from pybricks.tools import wait

def mission_three(r: robot):
    print("Running Mission 3")
    drivebase = r.robot
    left_attachment = r.lam
    right_attachment = r.ram
    drivebase.settings(straight_speed=STRAIGHT_SPEED, turn_rate=TURN_RATE)
    left_attachment.stop()
    right_attachment.stop()

    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        wait(10)
    drivebase.straight(492.4, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        wait(10)
    drivebase.straight(-70.1, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        wait(10)
    drivebase.straight(112.6, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        wait(10)
    drivebase.straight(-306.4, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()

################################
# KEEP THIS AT THE END OF THE FILE
# This redirects to running main.
################################
if __name__ == "__main__":
    from main import main
    main()

