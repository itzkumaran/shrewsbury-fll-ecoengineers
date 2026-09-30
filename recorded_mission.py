from pybricks.tools import run_task, wait

from robot import ATTACHMENT_SPEED, STRAIGHT_SPEED, TURN_RATE, robot


async def recorded_mission(r: robot):
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
        await wait(10)
    drivebase.straight(236.8, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.straight(-233.4, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.straight(83.1, wait=False)
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
    left_attachment.run_time(-ATTACHMENT_SPEED, 1683, wait=False)
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.run_time(ATTACHMENT_SPEED, 1740, wait=False)
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
    right_attachment.run_time(ATTACHMENT_SPEED, 1440, wait=False)
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.run_time(-ATTACHMENT_SPEED, 1617, wait=False)
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.turn(-94.4, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.straight(-117.0, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.turn(90.2, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.turn(-90.9, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.straight(108.5, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.turn(95.6, wait=False)
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.stop()
    left_attachment.stop()
    right_attachment.stop()
    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():
        await wait(10)
    drivebase.straight(-73.1, wait=False)
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
    left_attachment.stop()
    right_attachment.stop()


if __name__ == "__main__":
    r = robot()
    r.show_battery_level()
    run_task(recorded_mission(r))
