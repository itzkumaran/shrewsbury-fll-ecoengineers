################################################################################
# robot_check.py
#
# Runs the same experiments we used to calibrate lucky-chicken-2, so you can
# check any robot in about 1 minute. Results print in the VS Code terminal.
#
# BEFORE YOU RUN:
#   - Put the robot on the floor with about 50 cm of clear space in front
#     and behind it.
#   - Put a piece of tape next to one drive wheel to mark the START.
#   - Do not touch the robot after the program starts (the gyro calibrates).
#
# HOW TO RUN (from the project folder, with the .venv active):
#   python -m pybricksdev run ble --name lucky-chicken-2 robot_check.py
#
# Read docs/robot_experiments.md for what each test means.
#
# Author: ECO Engineers
# Date: 2026-09-27
################################################################################

import umath

from robot import robot
from pybricks.tools import run_task, wait

def result(name, ok, detail):
    """Print one test result as PASS or CHECK."""
    print("{:<8} {:<28} {}".format("PASS" if ok else "CHECK", name, detail))


async def run_robot_check(r):
    imu = r.hub.imu
    print("=== ROBOT CHECK: keep hands off for 3 seconds ===")
    await wait(3000)

    # Test 1: Gyro stays still when the robot is still.
    h = imu.heading()
    await wait(3000)
    still_drift = imu.heading() - h
    result("1. Gyro is steady", abs(still_drift) < 0.5,
           "moved {:+.2f} deg while sitting still".format(still_drift))

    # Test 2: Drive forward 300 mm and come back.
    h = imu.heading()
    d = r.robot.distance()
    r.robot.straight(300, wait=False)
    while not r.robot.done():
        await wait(10)
    await wait(300)
    fwd = r.robot.distance() - d
    fwd_turn = imu.heading() - h
    result("2. Drives 300 mm straight", abs(fwd - 300) <= 5 and abs(fwd_turn) < 2,
           "drove {} mm, turned {:+.1f} deg".format(fwd, fwd_turn))
    r.robot.straight(-300, wait=False)
    while not r.robot.done():
        await wait(10)
    await wait(300)

    # Test 3: Turn right 90, then left 90.
    h = imu.heading()
    r.robot.turn(90, wait=False)
    while not r.robot.done():
        await wait(10)
    await wait(500)
    right = imu.heading() - h
    result("3. Turn RIGHT 90", 88 <= right <= 92,
           "gyro says {:+.1f} deg (right is +)".format(right))
    h = imu.heading()
    r.robot.turn(-90, wait=False)
    while not r.robot.done():
        await wait(10)
    await wait(500)
    left = imu.heading() - h
    result("4. Turn LEFT 90", -92 <= left <= -88,
           "gyro says {:+.1f} deg (left is -)".format(left))

    # Test 5: Drift test - 5 trips forward and back.
    # We add up how far sideways the robot moved using the gyro angle.
    print("5. Drift test: 5 trips forward and back...")
    start_heading = imu.heading()
    sideways = 0.0
    for trip in range(5):
        for dist in (300, -300):
            last = r.robot.distance()
            r.robot.straight(dist, wait=False)
            while not r.robot.done():
                await wait(20)
                now = r.robot.distance()
                angle = umath.radians(imu.heading() - start_heading)
                sideways += (now - last) * umath.sin(angle)
                last = now
            await wait(300)
    end_turn = imu.heading() - start_heading
    result("5. Drift after 5 trips", abs(sideways) < 10 and abs(end_turn) < 2,
           "about {:+.1f} mm sideways (+ = right), facing {:+.1f} deg".format(sideways, end_turn))

    print("=== DONE ===")
    print("Now measure with a ruler: how far is the robot from your START tape?")
    print("Measured drift is usually about 1.5-2x the number above, because the")
    print("gyro can't see the wheels sliding sideways.")


if __name__ == "__main__":
    run_task(run_robot_check(robot()))
