################################################################
# hardware_test.py
#
# Simple hardware check: exercises the hub and every device found
# by check_ports.py, one step at a time:
#   1. Display "HELLO" and play a tune
#   2. Spin each motor a little (one at a time)
#   3. Read each color sensor
#   4. Drive forward/backward a short distance, turn right/left
#
# Each step prints what it is doing so the log shows exactly
# where something fails. Put the robot on the floor/table with
# ~20 cm of free space around it before running.
#
# Run: scripts/run-hub.sh "Lucky Chicken" hardware_test.py
#
# Port layout from ports_sample_output_lucky_chicken.out.
# If the wrong wheel spins in step 2, swap LEFT/RIGHT_DRIVE_PORT.
# If the robot spins instead of driving straight, flip one of the
# *_DRIVE_DIRECTION values.
#
################################################################

from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait

#############################################
# Configuration (Lucky Chicken)
#############################################
LEFT_DRIVE_PORT = Port.A  # SPIKE Large Motor
RIGHT_DRIVE_PORT = Port.E  # SPIKE Large Motor
LEFT_DRIVE_DIRECTION = Direction.COUNTERCLOCKWISE
RIGHT_DRIVE_DIRECTION = Direction.CLOCKWISE

ATTACHMENT_PORTS = [("C", Port.C), ("D", Port.D)]  # SPIKE Medium Motors
COLOR_SENSOR_PORTS = [("B", Port.B), ("F", Port.F)]  # SPIKE Color Sensors

TIRE_DIAMETER = 56  # mm
AXLE_TRACK = 113  # mm

MOTOR_TEST_SPEED = 200  # deg/sec
MOTOR_TEST_ANGLE = 90  # degrees each way
DRIVE_DISTANCE = 100  # mm
TURN_ANGLE = 90  # degrees


def step(hub, number, message):
    print("[" + str(number) + "]", message)
    hub.display.number(number)
    wait(500)


def test_hub(hub):
    step(hub, 1, "Display HELLO and play a tune")
    hub.display.text("HELLO", 300, 50)
    hub.speaker.volume(50)
    hub.speaker.play_notes(["C4/8", "E4/8", "G4/8", "C5/4"], tempo=120)
    print("    battery:", hub.battery.voltage(), "mV")


def test_motor(hub, number, name, port, direction=Direction.CLOCKWISE):
    step(hub, number, "Spin " + name)
    try:
        motor = Motor(port, positive_direction=direction)
        motor.run_angle(MOTOR_TEST_SPEED, MOTOR_TEST_ANGLE)
        motor.run_angle(MOTOR_TEST_SPEED, -MOTOR_TEST_ANGLE)
        print("    OK")
        return motor
    except OSError as e:
        print("    FAILED:", e)
        return None


def test_color_sensor(hub, number, letter, port):
    step(hub, number, "Read color sensor on port " + letter)
    try:
        sensor = ColorSensor(port)
        sensor.lights.on(100)
        wait(300)
        print("    color:", sensor.color(), "| reflection:", sensor.reflection(), "%")
        sensor.lights.off()
    except OSError as e:
        print("    FAILED:", e)


def test_drive(hub, number, left, right):
    if left is None or right is None:
        print("[" + str(number) + "] Skipping drive test: a drive motor failed")
        return
    drive = DriveBase(left, right, TIRE_DIAMETER, AXLE_TRACK)
    drive.settings(straight_speed=100, turn_rate=60)

    step(hub, number, "Drive forward " + str(DRIVE_DISTANCE) + " mm")
    drive.straight(DRIVE_DISTANCE)
    step(hub, number + 1, "Drive backward " + str(DRIVE_DISTANCE) + " mm")
    drive.straight(-DRIVE_DISTANCE)
    step(hub, number + 2, "Turn right " + str(TURN_ANGLE) + " deg")
    drive.turn(TURN_ANGLE)
    step(hub, number + 3, "Turn left " + str(TURN_ANGLE) + " deg")
    drive.turn(-TURN_ANGLE)
    drive.stop()


def main():
    hub = PrimeHub()
    print("=== Hardware test ===")

    test_hub(hub)

    left = test_motor(hub, 2, "LEFT drive motor (port A)", LEFT_DRIVE_PORT, LEFT_DRIVE_DIRECTION)
    right = test_motor(hub, 3, "RIGHT drive motor (port E)", RIGHT_DRIVE_PORT, RIGHT_DRIVE_DIRECTION)

    number = 4
    for letter, port in ATTACHMENT_PORTS:
        test_motor(hub, number, "attachment motor (port " + letter + ")", port)
        number += 1

    for letter, port in COLOR_SENSOR_PORTS:
        test_color_sensor(hub, number, letter, port)
        number += 1

    test_drive(hub, number, left, right)

    hub.display.text("DONE")
    hub.speaker.beep(1000, 200)
    print("=== Hardware test done ===")


if __name__ == "__main__":
    main()
