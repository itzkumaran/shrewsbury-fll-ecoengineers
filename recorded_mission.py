import umath

from pybricks.tools import wait

from robot import robot, TIRE_DIAMETER

# Must match xbox_controller.py's DRIVE_SPEED/TURN_RATE/ATTACHMENT_SPEED so
# recordings made with the controller replay identically here.
DRIVE_SPEED = 250 / 360 * umath.pi * TIRE_DIAMETER
TURN_RATE = 90
ATTACHMENT_SPEED = 120


def recorded_mission(r: robot):
    drivebase = r.robot
    left_attachement = r.lam

    drivebase.stop()
    left_attachement.stop()
    wait(330)
    drivebase.drive(-DRIVE_SPEED, 0)
    left_attachement.stop()
    wait(1770)
    drivebase.stop()
    left_attachement.stop()
    wait(180)
    drivebase.drive(DRIVE_SPEED, 0)
    left_attachement.stop()
    wait(1830)
    drivebase.stop()
    left_attachement.stop()
    wait(150)
    drivebase.drive(0, -TURN_RATE)
    left_attachement.stop()
    wait(1407)
    drivebase.stop()
    left_attachement.stop()
    wait(150)
    drivebase.drive(0, TURN_RATE)
    left_attachement.stop()
    wait(1529)
    drivebase.stop()
    left_attachement.stop()
    wait(180)
    drivebase.drive(DRIVE_SPEED, 0)
    left_attachement.stop()
    wait(1020)
    drivebase.stop()
    left_attachement.stop()
    wait(95)
    drivebase.stop()
    left_attachement.run(ATTACHMENT_SPEED)
    wait(990)
    drivebase.stop()
    left_attachement.run(-ATTACHMENT_SPEED)
    wait(1285)
    drivebase.stop()
    left_attachement.stop()


if __name__ == "__main__":
    r = robot()
    r.show_battery_level()
    recorded_mission(r)
