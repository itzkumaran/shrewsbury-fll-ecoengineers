import umath

from pybricks.iodevices import XboxController
from pybricks.parameters import Button, Direction, Port
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, multitask, run_task, wait

# Wheel size, used to convert motor angle to distance driven.
WHEEL_DIAMETER = 55.5  # mm

# Distance between the centers of the left and right wheels, used to
# convert wheel angle to the angle the robot itself turned during a
# pivot turn, and by the drive base for gyro-corrected driving.
TRACK_WIDTH = 80  # mm

# Set up all devices.
left = Motor(Port.B, Direction.CLOCKWISE)
right = Motor(Port.F, Direction.COUNTERCLOCKWISE)
left_attachement = Motor(Port.C, Direction.CLOCKWISE)
controller = XboxController()

# Treat wherever the attachements happen to be at startup as 0, so
# their angle is relative to the start of the program rather than
# whatever the motor's absolute encoder reads.
left_attachement.reset_angle(0)

# A high acceleration limit lets the controller apply torque quickly
# for a step, instead of ramping up gently and possibly not
# developing enough force to overcome friction within just 5 degrees.
left_attachement.control.limits(acceleration=1000)

# Used for forward/reverse driving, so the gyro can keep us driving
# straight. Left/right pivot turns and diagonal turns still drive the
# left/right motors directly, which automatically cancels the drive
# base's current maneuver.
drivebase = DriveBase(left, right, WHEEL_DIAMETER, TRACK_WIDTH)
drivebase.use_gyro(True)

# Linear speed for forward/reverse that matches the previous 250 deg/s
# wheel speed used for turning.
DRIVE_SPEED = 250 / 360 * umath.pi * WHEEL_DIAMETER  # mm/s
TURN_RATE = 90  # deg/s, limited to make pivot turns smoother
RECORD_SAMPLE_MS = 10
ATTACHMENT_SPEED = 120  # deg/s for smooth, moderate attachment movement

# Movement recording is kept in memory for the current program run.
recording = []
is_recording = False
is_replaying = False
recording_sample = None
watch = StopWatch()

# Names of the dpad directions, for debug printing.
DIRECTION_NAMES = {
    1: "Forward",
    2: "Forward / Right",
    3: "Right",
    4: "Reverse / Right",
    5: "Reverse",
    6: "Reverse / Left",
    7: "Left",
    8: "Forward / Left",
}


def apply_direction(direction):
    if direction == 1:
        drivebase.drive(-DRIVE_SPEED, 0)
    elif direction == 3:
        drivebase.drive(0, -TURN_RATE)
    elif direction == 5:
        drivebase.drive(DRIVE_SPEED, 0)
    elif direction == 7:
        drivebase.drive(0, TURN_RATE)
    else:
        drivebase.stop()


def print_recording_code():
    if not recording:
        print("No movement recording available")
        return

    print("----- RECORDED MISSION CODE -----")
    print("# Paste this into recorded_mission.py or a mission file")
    print("def recorded_mission(r: robot):")
    print("    drivebase = r.robot")
    print("    left_attachement = r.lam")
    print("")
    for sample, duration_ms in recording:
        direction = sample % 8
        attachment_direction = sample // 8 - 1

        if direction == 1:
            print("    drivebase.drive(-DRIVE_SPEED, 0)")
        elif direction == 3:
            print("    drivebase.drive(0, -TURN_RATE)")
        elif direction == 5:
            print("    drivebase.drive(DRIVE_SPEED, 0)")
        elif direction == 7:
            print("    drivebase.drive(0, TURN_RATE)")
        else:
            print("    drivebase.stop()")

        if attachment_direction == 1:
            print("    left_attachement.run(ATTACHMENT_SPEED)")
        elif attachment_direction == -1:
            print("    left_attachement.run(-ATTACHMENT_SPEED)")
        else:
            print("    left_attachement.stop()")
        print("    wait({0})".format(duration_ms))

    print("    drivebase.stop()")
    print("    left_attachement.stop()")
    print("----- END RECORDED MISSION CODE -----")


async def replay_recording():
    global is_replaying

    if not recording:
        print("No movement recording available")
        return

    print("Replaying movement recording")
    is_replaying = True
    try:
        for sample, duration_ms in recording:
            direction = sample % 8
            attachment_direction = sample // 8 - 1

            apply_direction(direction)
            if attachment_direction:
                left_attachement.run(ATTACHMENT_SPEED * attachment_direction)
            else:
                left_attachement.stop()

            await wait(duration_ms)
        print("Replay complete")
    finally:
        is_replaying = False
        drivebase.stop()
        left_attachement.stop()

async def main1():
    global is_recording, recording_sample

    # This main task will handle driving and the motors that power
    # the left and right attachements.
    left.control.limits(acceleration=2500)
    right.control.limits(acceleration=2500)
    print_counter = 0
    active_direction = 0
    left_start = left.angle()
    right_start = right.angle()
    last_drive_value = None
    previous_y_pressed = False
    previous_a_pressed = False
    while True:
        pressed = controller.buttons.pressed()
        y_pressed = Button.Y in pressed
        a_pressed = Button.A in pressed

        if y_pressed and not previous_y_pressed:
            if not is_recording:
                is_recording = True
                recording.clear()
                recording_sample = None
                watch.reset()
                print("Recording started")
            else:
                is_recording = False
                if recording_sample is not None:
                    elapsed = watch.time()
                    if elapsed > 0:
                        recording.append((recording_sample, elapsed))
                    recording_sample = None
                print("Recording stopped: {0} actions".format(len(recording)))
                print_recording_code()

        if a_pressed and not previous_a_pressed and not is_recording and not is_replaying:
            drivebase.stop()
            left_attachement.stop()
            await replay_recording()

        previous_y_pressed = y_pressed
        previous_a_pressed = a_pressed

        if is_replaying:
            await wait(10)
            continue

        await wait(5)
        # Only Forward (1), Right (3), Reverse (5), and Left (7) drive
        # the robot. Any other dpad tap (the diagonals) is ignored
        # entirely, as if the dpad were untouched.
        direction = controller.dpad()
        if direction not in (1, 3, 5, 7):
            direction = 0
        # The dpad direction selects which way we drive. Releasing the
        # dpad (direction 0) does not reset the distance, so inching
        # ahead in the same direction with several short presses still
        # adds up. Only pressing an actual different direction resets it.
        if direction and direction != active_direction:
            active_direction = direction
            left_start = left.angle()
            right_start = right.angle()
            print("Direction: {0}".format(DIRECTION_NAMES[direction]))
        # Print to the debug screen every 500 ms, measured since the
        # current direction was first selected. For Left/Right (pivot
        # turns), print the angle the robot turned. Otherwise, print
        # the distance driven.
        print_counter += 1
        if print_counter >= 500:
            print_counter = 0
            # Don't print distance/angle while the left or right
            # attachement is being operated, and don't print it again
            # if it hasn't changed since the last time.
            using_other_motor = (Button.RB in pressed or Button.LB in pressed
                                  or Button.X in pressed or Button.B in pressed)
            if not using_other_motor:
                left_delta = left.angle() - left_start
                right_delta = right.angle() - right_start
                if active_direction in (3, 7):
                    wheel_angle = abs(left_delta - right_delta) / 2
                    # During a pivot turn, each wheel traces an arc
                    # around the robot's center, which is
                    # TRACK_WIDTH / 2 away. Scale the wheel's own
                    # rotation by the ratio of wheel diameter to track
                    # width to get the robot's rotation.
                    drive_value = round(wheel_angle * WHEEL_DIAMETER / TRACK_WIDTH, 1)
                    if drive_value != last_drive_value:
                        last_drive_value = drive_value
                        print("Angle turned: {0:.1f} deg".format(drive_value))
                else:
                    average_angle = (left_delta + right_delta) / 2
                    drive_value = round(average_angle / 360 * umath.pi * WHEEL_DIAMETER / 10, 1)
                    if drive_value != last_drive_value:
                        last_drive_value = drive_value
                        print("Distance driven: {0:.1f} cm".format(drive_value))
        # Use the direction pad for driving.
        if direction == 1:
            # Reverse. Use the drive base so the gyro keeps us
            # driving straight.
            drivebase.drive(-DRIVE_SPEED, 0)
        elif direction == 3:
            # Right
            drivebase.drive(0, -TURN_RATE)
        elif direction == 5:
            # Forward. Use the drive base so the gyro keeps us
            # driving straight.
            drivebase.drive(DRIVE_SPEED, 0)
        elif direction == 7:
            # Left
            drivebase.drive(0, TURN_RATE)
        else:
            # Nothing (or an ignored diagonal tap), so stop.
            drivebase.stop()

        if is_recording:
            attachment_direction = 0
            if Button.RB in pressed:
                attachment_direction = 1
            elif Button.LB in pressed:
                attachment_direction = -1
            sample = direction + 8 * (attachment_direction + 1)
            if recording_sample is None:
                recording_sample = sample
                watch.reset()
            elif sample != recording_sample:
                elapsed = watch.time()
                watch.reset()
                if elapsed > 0:
                    recording.append((recording_sample, elapsed))
                recording_sample = sample

async def attachment_stepper(motor, label, positive_button, negative_button):
    while True:
        if is_replaying:
            await wait(10)
            continue
        pressed = controller.buttons.pressed()
        if positive_button in pressed:
            motor.run(ATTACHMENT_SPEED)
        elif negative_button in pressed:
            motor.run(-ATTACHMENT_SPEED)
        else:
            motor.stop()
        await wait(5)

async def main():
    await multitask(
        main1(),
        attachment_stepper(left_attachement, "Left attachement", Button.RB, Button.LB),
    )

run_task(main())
