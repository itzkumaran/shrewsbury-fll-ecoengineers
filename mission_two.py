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
    drivebase = r.robot
    left_attachement = r.lam
    start = r.hub.imu.heading()  # headings below are measured from here
    drivebase.stop()
    wait(1255)
    drivebase.settings(straight_speed=122.2, turn_rate=45)
    r.face(start + 0.0)
    drivebase.straight(148.1)
    drivebase.stop()
    wait(210)
    r.face(start + 52.3)
    drivebase.stop()
    wait(390)
    r.face(start + 54.4)
    drivebase.stop()
    wait(660)
    drivebase.straight(163.0)
    drivebase.stop()
    wait(155)
    left_attachement.run_time(120, 1050, wait=False)
    while not left_attachement.done():
        wait(10)
    drivebase.stop()
    wait(295)
    r.face(start + 54.2)
    drivebase.straight(47.9)
    drivebase.stop()
    wait(180)
    r.face(start + 54.3)
    drivebase.straight(31.3)
    drivebase.stop()
    wait(990)
    r.face(start + 55.5)
    drivebase.stop()
    wait(390)
    r.face(start + 55.5)
    drivebase.stop()
    wait(390)
    r.face(start + 56.3)
    drivebase.stop()
    wait(508)
    drivebase.straight(2.9)
    drivebase.stop()
    wait(330)
    r.face(start + 56.2)
    drivebase.straight(5.4)
    drivebase.stop()
    wait(450)
    r.face(start + 56.7)
    drivebase.straight(19.3)
    drivebase.stop()
    wait(1355)
    left_attachement.run_time(-120, 150, wait=False)
    while not left_attachement.done():
        wait(10)
    drivebase.stop()
    wait(240)
    left_attachement.run_time(-120, 300, wait=False)
    while not left_attachement.done():
        wait(10)
    drivebase.stop()
    wait(750)
    left_attachement.run_time(-120, 565, wait=False)
    while not left_attachement.done():
        wait(10)
    left_attachement.run_time(-120, 2883, wait=False)
    r.face(start + 56.8)
    drivebase.straight(-336.0)
    while not left_attachement.done():
        wait(10)
    r.face(start + 56.9)
    drivebase.straight(-21.5)
    drivebase.stop()
    wait(745)
    drivebase.stop()
    left_attachement.stop()
    
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
