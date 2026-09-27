import umath

from pybricks.tools import wait

from robot import TIRE_DIAMETER, robot

ACTION_SETTLE_MS = 100
DRIVE_SPEED = 250 / 360 * umath.pi * TIRE_DIAMETER
TURN_RATE = 45


def recorded_mission(r: robot):
    drivebase = r.robot
    left_attachement = r.lam

    drivebase.settings(straight_speed=DRIVE_SPEED, turn_rate=TURN_RATE)
    drivebase.stop()
    left_attachement.stop()
    drivebase.straight(-232.6)
    wait(ACTION_SETTLE_MS)
    drivebase.turn(66.3)
    wait(ACTION_SETTLE_MS)
    drivebase.straight(-462.5)
    wait(ACTION_SETTLE_MS)
    drivebase.turn(-35.3)
    wait(ACTION_SETTLE_MS)
    drivebase.straight(-149.1)
    wait(ACTION_SETTLE_MS)
    drivebase.turn(-31.7)
    wait(ACTION_SETTLE_MS)
    drivebase.straight(-193.8)
    wait(ACTION_SETTLE_MS)
    drivebase.turn(-30.2)
    wait(ACTION_SETTLE_MS)
    drivebase.straight(-260.2)
    wait(ACTION_SETTLE_MS)
    drivebase.straight(39.1)
    wait(ACTION_SETTLE_MS)
    drivebase.turn(74.5)
    wait(ACTION_SETTLE_MS)
    drivebase.turn(-136.6)
    wait(ACTION_SETTLE_MS)
    drivebase.straight(-201.8)
    wait(ACTION_SETTLE_MS)
    drivebase.turn(-27.6)
    wait(ACTION_SETTLE_MS)
    drivebase.straight(-162.2)
    wait(ACTION_SETTLE_MS)
    drivebase.turn(-19.6)
    wait(ACTION_SETTLE_MS)
    drivebase.straight(-421.7)
    wait(ACTION_SETTLE_MS)
    drivebase.stop()
    left_attachement.stop()


if __name__ == "__main__":
    r = robot()
    r.show_battery_level()
    recorded_mission(r)
