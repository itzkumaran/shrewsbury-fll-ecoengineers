import umath

from pybricks.tools import run_task, wait

from robot import TIRE_DIAMETER, robot

DRIVE_SPEED = 250 / 360 * umath.pi * TIRE_DIAMETER
TURN_RATE = 45


async def recorded_mission(r: robot):
    drivebase = r.robot
    left_attachment = r.lam
    right_attachment = r.ram
    drivebase.settings(straight_speed=DRIVE_SPEED, turn_rate=TURN_RATE)
    left_attachment.stop()
    right_attachment.stop()

    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.straight(233.6, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.straight(-232.9, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.straight(76.0, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.turn(-67.4, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.turn(65.4, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.straight(-40.8, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.run_time(-120, 1710, wait=False)
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.run_time(120, 1919, wait=False)
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.run_time(120, 1530, wait=False)
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.run_time(-120, 1558, wait=False)
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()


if __name__ == "__main__":
    r = robot()
    r.show_battery_level()
    run_task(recorded_mission(r))
