import umath

from pybricks.iodevices import XboxController
from pybricks.parameters import Button
from pybricks.tools import StopWatch, multitask, run_task, wait

from robot import (
    AXLE_TRACK,
    TIRE_DIAMETER,
    robot,
)
from recorded_mission import recorded_mission

# Initialize robot instance to configure PrimeHub gyro orientation,
# drive base geometry, and motor directions centrally from robot.py.
r = robot()
left = r.ldm
right = r.rdm
left_attachment = r.lam
right_attachment = r.ram
drivebase = r.robot
controller = XboxController()

WHEEL_DIAMETER = TIRE_DIAMETER  # mm
TRACK_WIDTH = AXLE_TRACK  # mm

# Treat wherever the attachments happen to be at startup as 0.
left_attachment.reset_angle(0)
left_attachment.control.limits(acceleration=1000)
right_attachment.reset_angle(0)
right_attachment.control.limits(acceleration=1000)

# Linear speed for forward/reverse that matches the previous 250 deg/s
# wheel speed used for turning.
DRIVE_SPEED = 250 / 360 * umath.pi * WHEEL_DIAMETER  # mm/s
TURN_RATE = 45  # deg/s, limited to make pivot turns smoother
RECORD_SAMPLE_MS = 10
ATTACHMENT_SPEED = 120  # deg/s for smooth, moderate attachment movement
TRIGGER_PRESS_THRESHOLD = 50

# Movement recording is kept in memory for the current program run.
recording = []
is_recording = False
is_replaying = False
recording_sample = None
recording_left_start = 0
recording_right_start = 0
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
        r.drive_straight(DRIVE_SPEED)
    elif direction == 3:
        r.drive_turn(TURN_RATE)
    elif direction == 5:
        r.drive_straight(-DRIVE_SPEED)
    elif direction == 7:
        r.drive_turn(-TURN_RATE)
    else:
        r.stop_drive()


def append_recording_segment(sample, duration_ms, left_start, right_start):
    if duration_ms > 0:
        recording.append((
            sample,
            duration_ms,
            left.angle() - left_start,
            right.angle() - right_start,
        ))


def attachment_directions(sample):
    attachment_states = sample // 8
    return attachment_states % 3 - 1, attachment_states // 3 - 1


def print_recording_code():
    if not recording:
        print("No movement recording available")
        return

    print("----- RECORDED MISSION CODE -----")
    print("# Paste this into recorded_mission.py or a mission file")
    print("import umath")
    print("from pybricks.tools import run_task, wait")
    print("from robot import AXLE_TRACK, TIRE_DIAMETER, robot")
    print("WHEEL_DIAMETER = TIRE_DIAMETER")
    print("TRACK_WIDTH = AXLE_TRACK")
    print("DRIVE_SPEED = {0}".format(DRIVE_SPEED))
    print("TURN_RATE = {0}".format(TURN_RATE))
    print("ATTACHMENT_SPEED = {0}".format(ATTACHMENT_SPEED))
    print("")
    print("async def recorded_mission(r: robot):")
    print("    drivebase = r.robot")
    print("    left_attachment = r.lam")
    print("    right_attachment = r.ram")
    print("    drivebase.settings(straight_speed=DRIVE_SPEED, turn_rate=TURN_RATE)")
    print("    left_attachment.stop()")
    print("    right_attachment.stop()")
    print("")
    for sample, duration_ms, left_delta, right_delta in recording:
        direction = sample % 8
        left_attachment_direction, right_attachment_direction = attachment_directions(sample)
        distance_mm = (
            (left_delta + right_delta) / 2 / 360
            * umath.pi * WHEEL_DIAMETER
        )
        turn_angle = (
            (left_delta - right_delta) * WHEEL_DIAMETER
            / (2 * TRACK_WIDTH)
        )

        if direction in (1, 5):
            print("    drivebase.straight({0:.1f}, wait=False)".format(distance_mm))
        elif direction in (3, 7):
            print("    drivebase.turn({0:.1f}, wait=False)".format(turn_angle))
        else:
            print("    drivebase.stop()")

        if left_attachment_direction:
            print("    left_attachment.run_time({0}, {1}, wait=False)".format(
                ATTACHMENT_SPEED * left_attachment_direction, duration_ms
            ))
        else:
            print("    left_attachment.stop()")
        if right_attachment_direction:
            print("    right_attachment.run_time({0}, {1}, wait=False)".format(
                ATTACHMENT_SPEED * right_attachment_direction, duration_ms
            ))
        else:
            print("    right_attachment.stop()")
        print("    while not drivebase.done() or not left_attachment.done() or not right_attachment.done():")
        print("        wait(10)")

    print("    drivebase.stop()")
    print("    left_attachment.stop()")
    print("    right_attachment.stop()")
    print("")
    print("if __name__ == \"__main__\":")
    print("    r = robot()")
    print("    r.show_battery_level()")
    print("    run_task(recorded_mission(r))")
    print("----- END RECORDED MISSION CODE -----")


async def replay_recording():
    global is_replaying

    if not recording:
        print("No movement recording available")
        return

    print("Replaying movement recording")
    is_replaying = True
    try:
        drivebase.settings(straight_speed=DRIVE_SPEED, turn_rate=TURN_RATE)
        for sample, duration_ms, left_delta, right_delta in recording:
            direction = sample % 8
            left_attachment_direction, right_attachment_direction = attachment_directions(sample)

            distance_mm = (
                (left_delta + right_delta) / 2 / 360
                * umath.pi * WHEEL_DIAMETER
            )
            turn_angle = (
                (left_delta - right_delta) * WHEEL_DIAMETER
                / (2 * TRACK_WIDTH)
            )
            watch.reset()
            if direction == 1:
                drivebase.straight(distance_mm, wait=False)
            elif direction == 3:
                drivebase.turn(turn_angle, wait=False)
            elif direction == 5:
                drivebase.straight(distance_mm, wait=False)
            elif direction == 7:
                drivebase.turn(turn_angle, wait=False)
            else:
                r.stop_drive()

            if left_attachment_direction:
                left_attachment.run(ATTACHMENT_SPEED * left_attachment_direction)
            else:
                left_attachment.stop()
            if right_attachment_direction:
                right_attachment.run(ATTACHMENT_SPEED * right_attachment_direction)
            else:
                right_attachment.stop()

            while watch.time() < duration_ms or not drivebase.done():
                await wait(10)
            left_attachment.stop()
            right_attachment.stop()
        print("Replay complete")
    finally:
        is_replaying = False
        r.stop_drive()
        left_attachment.stop()
        right_attachment.stop()

async def main1():
    global is_recording, recording_sample
    global is_replaying
    global recording_left_start, recording_right_start

    print_counter = 0
    active_direction = 0
    left_start = left.angle()
    right_start = right.angle()
    last_drive_value = None
    previous_y_pressed = False
    previous_a_pressed = False
    previous_lt_pressed = False
    while True:
        pressed = controller.buttons.pressed()
        y_pressed = Button.Y in pressed
        a_pressed = Button.A in pressed
        left_trigger, _ = controller.triggers()
        lt_pressed = left_trigger >= TRIGGER_PRESS_THRESHOLD

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
                        append_recording_segment(
                            recording_sample,
                            elapsed,
                            recording_left_start,
                            recording_right_start,
                        )
                    recording_sample = None
                print("Recording stopped: {0} actions".format(len(recording)))
                print_recording_code()

        if a_pressed and not previous_a_pressed and not is_recording and not is_replaying:
            drivebase.stop()
            left_attachment.stop()
            right_attachment.stop()
            await replay_recording()

        if lt_pressed and not previous_lt_pressed and not is_recording and not is_replaying:
            print("Running recorded mission")
            is_replaying = True
            drivebase.stop()
            left_attachment.stop()
            right_attachment.stop()
            try:
                await recorded_mission(r)
            finally:
                r.stop_drive()
                left_attachment.stop()
                right_attachment.stop()
                is_replaying = False

        previous_y_pressed = y_pressed
        previous_a_pressed = a_pressed
        previous_lt_pressed = lt_pressed

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
        if is_recording:
            left_attachment_direction = 0
            right_attachment_direction = 0
            if Button.RB in pressed:
                left_attachment_direction = 1
            elif Button.LB in pressed:
                left_attachment_direction = -1
            if Button.X in pressed:
                right_attachment_direction = 1
            elif Button.B in pressed:
                right_attachment_direction = -1
            attachment_states = (
                left_attachment_direction + 1
                + 3 * (right_attachment_direction + 1)
            )
            sample = direction + 8 * attachment_states
            if recording_sample is None:
                recording_sample = sample
                recording_left_start = left.angle()
                recording_right_start = right.angle()
                watch.reset()
            elif sample != recording_sample:
                elapsed = watch.time()
                append_recording_segment(
                    recording_sample,
                    elapsed,
                    recording_left_start,
                    recording_right_start,
                )
                recording_sample = sample
                recording_left_start = left.angle()
                recording_right_start = right.angle()
                watch.reset()
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
            # Forward. Use the drive base so the gyro keeps us
            # driving straight.
            r.drive_straight(DRIVE_SPEED)
        elif direction == 3:
            # Right
            r.drive_turn(TURN_RATE)
        elif direction == 5:
            # Reverse. Use the drive base so the gyro keeps us
            # driving straight.
            r.drive_straight(-DRIVE_SPEED)
        elif direction == 7:
            # Left
            r.drive_turn(-TURN_RATE)
        else:
            # Nothing (or an ignored diagonal tap), so stop.
            r.stop_drive()

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
        attachment_stepper(left_attachment, "Left attachment", Button.RB, Button.LB),
        attachment_stepper(right_attachment, "Right attachment", Button.X, Button.B),
    )

run_task(main())
