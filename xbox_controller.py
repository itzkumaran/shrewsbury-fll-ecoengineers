import umath

from pybricks.iodevices import XboxController
from pybricks.parameters import Button
from pybricks.tools import StopWatch, multitask, run_task, wait

from robot import (
    AXLE_TRACK,
    TIRE_DIAMETER,
    robot,
)

# Initialize robot instance to configure PrimeHub gyro orientation,
# drive base geometry, and motor directions centrally from robot.py.
r = robot()
left = r.ldm
right = r.rdm
left_attachement = r.lam
drivebase = r.robot


def connect_controller(max_ms=60000):
    """Connect to the Xbox controller, retrying for up to max_ms.

    One connection attempt often fails after a few seconds, especially
    while the laptop is also connected to the hub over Bluetooth, so keep
    trying instead of stopping with an error on the first try.
    """
    sw = StopWatch()
    print("Connecting to Xbox controller...")
    print("  Hold the pair button on the controller until the Xbox logo flashes fast.")
    while True:
        try:
            c = XboxController(timeout=10000)
            print("Xbox controller connected after {0} s".format(sw.time() // 1000))
            return c
        except OSError:
            if sw.time() > max_ms:
                print("Could not connect to the Xbox controller.")
                print("  Check it is charged, not paired to another device,")
                print("  and the logo is flashing fast. Then run again.")
                raise
            print("  still looking... ({0} s)".format(sw.time() // 1000))
            wait(500)


controller = connect_controller()


def reconnect_controller(max_ms=60000):
    """The controller dropped: stop the robot and reconnect instead of crashing."""
    r.stop_drive()
    left_attachement.stop()
    print("Xbox controller disconnected - reconnecting (press its pair button if needed)...")
    sw = StopWatch()
    while True:
        try:
            controller.connect()
            print("Xbox controller reconnected")
            return
        except OSError:
            if sw.time() > max_ms:
                print("Could not reconnect the Xbox controller.")
                raise
            wait(500)


def controller_pressed():
    try:
        return controller.buttons.pressed()
    except OSError:
        reconnect_controller()
        return controller.buttons.pressed()


def controller_dpad():
    try:
        return controller.dpad()
    except OSError:
        reconnect_controller()
        return controller.dpad()

WHEEL_DIAMETER = TIRE_DIAMETER  # mm
TRACK_WIDTH = AXLE_TRACK  # mm

# Treat wherever the attachments happen to be at startup as 0.
left_attachement.reset_angle(0)
left_attachement.control.limits(acceleration=1000)

# Linear speed for forward/reverse that matches the previous 250 deg/s
# wheel speed used for turning.
DRIVE_SPEED = 250 / 360 * umath.pi * WHEEL_DIAMETER  # mm/s
TURN_RATE = 45  # deg/s, limited to make pivot turns smoother
RECORD_SAMPLE_MS = 10
ATTACHMENT_SPEED = 120  # deg/s for smooth, moderate attachment movement
ACTION_SETTLE_MS = 100

# Speed levels, cycled with the X button: (drive mm/s, turn deg/s).
# Level 2 (index 1) is the normal speed and is used at startup.
SPEED_LEVELS = [
    (60, 22),                # 1 Slow
    (DRIVE_SPEED, TURN_RATE),  # 2 Normal
    (250, 60),               # 3 Fast (turns capped at 60 deg/s: 90 made the wheels slip)
]
speed_level = 1  # index into SPEED_LEVELS

# Acceleration used while driving with the controller, recording and
# replaying (mm/s^2). Quicker than robot.py's 500 so direction changes feel
# snappy: forward-to-reverse took 0.52 s at 500 and 0.30 s at 1000.
# Replay and the printed mission code use the same value so they match.
CONTROLLER_STRAIGHT_ACCEL = 1000
drivebase.settings(straight_acceleration=CONTROLLER_STRAIGHT_ACCEL)

# Movement recording is kept in memory for the current program run.
recording = []
is_recording = False
is_replaying = False
recording_sample = None
recording_left_start = 0
recording_right_start = 0
recording_heading_start = 0
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


def append_recording_segment(sample, duration_ms, left_start, right_start, heading_start):
    if duration_ms > 0:
        recording.append((
            sample,
            duration_ms,
            left.angle() - left_start,
            right.angle() - right_start,
            r.hub.imu.heading() - heading_start,
        ))


def recording_steps():
    """Turn raw recording segments into replay steps.

    Each step is [direction, attachment_direction, duration_ms,
    distance_mm, turn_deg, speed_level, heading_start, heading_end].

    heading_start / heading_end are the gyro heading at the start and end
    of the step, measured from where the recording started. Replay aims at
    these absolute headings, so a small error in one turn does not carry
    into every move after it.

    - Motion measured during a "stop" segment is the robot still rolling
      (coasting) after the D-pad was released, so it is added back to the
      move before it. Otherwise replay comes up short on every move.
    - Turns use the gyro heading change, which is more accurate than
      estimating the angle from the wheel encoders.
    """
    steps = []
    for sample, duration_ms, left_delta, right_delta, heading_delta in recording:
        level = sample // 24
        direction = sample % 24 % 8
        attachment_direction = sample % 24 // 8 - 1
        distance_mm = (
            (left_delta + right_delta) / 2 / 360
            * umath.pi * WHEEL_DIAMETER
        )
        if direction == 0 and steps and steps[-1][0] != 0:
            steps[-1][3] += distance_mm
            steps[-1][4] += heading_delta
            distance_mm = 0
            heading_delta = 0
        steps.append([direction, attachment_direction, duration_ms,
                      distance_mm, heading_delta, level])
    # Add up the heading changes to get each step's absolute heading.
    heading = 0.0
    for step in steps:
        step.append(heading)       # heading_start
        heading += step[4]
        step.append(heading)       # heading_end
    return steps


async def face_heading(target):
    """Turn in place (if needed) until the gyro reads the target heading."""
    error = target - r.hub.imu.heading()
    if abs(error) >= 0.5:
        drivebase.reset(0, r.hub.imu.heading())
        drivebase.turn(error, wait=False)
        while not drivebase.done():
            await wait(10)


def print_recording_code():
    if not recording:
        print("No movement recording available")
        return

    print("----- RECORDED MISSION CODE -----")
    print("# Paste the lines below inside a mission function, e.g. def mission_two(r: robot):")
    print("# (they only use r, so no extra imports or constants are needed)")
    print("    drivebase = r.robot")
    print("    left_attachement = r.lam")
    print("    start = r.hub.imu.heading()  # headings below are measured from here")
    last_level = None
    last_face = None  # skip repeating the same face() target twice in a row
    for (direction, attachment_direction, duration_ms, distance_mm, turn_deg, level,
         heading_start, heading_end) in recording_steps():
        if direction in (1, 3, 5, 7) and level != last_level:
            print("    drivebase.settings(straight_speed={0:.1f}, straight_acceleration={1}, turn_rate={2})".format(
                SPEED_LEVELS[level][0], CONTROLLER_STRAIGHT_ACCEL, SPEED_LEVELS[level][1]))
            last_level = level
        if attachment_direction:
            print("    left_attachement.run_time({0}, {1}, wait=False)".format(
                ATTACHMENT_SPEED * attachment_direction, duration_ms))

        if direction in (1, 5):
            target = "{0:.1f}".format(heading_start)
            if target != last_face:
                print("    r.face(start + {0})".format(target))
                last_face = target
            print("    drivebase.straight({0:.1f})".format(distance_mm))
        elif direction in (3, 7):
            last_face = "{0:.1f}".format(heading_end)
            print("    r.face(start + {0})".format(last_face))
        elif not attachment_direction:
            # Keep the pause, same length as in the recording.
            print("    drivebase.stop()")
            print("    wait({0})".format(duration_ms))
            continue

        if attachment_direction:
            print("    while not left_attachement.done():")
            print("        wait(10)")

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
    saved_settings = drivebase.settings()
    try:
        # Each move replays at the speed it was recorded at (X button level),
        # so missions don't run faster than the robot was driven.
        # Headings are measured from where the replay starts, so put the
        # robot at the same start spot and direction as the recording.
        start_heading = r.hub.imu.heading()
        for (direction, attachment_direction, duration_ms, distance_mm, turn_deg, level,
             heading_start, heading_end) in recording_steps():
            moving = direction in (1, 3, 5, 7)

            watch.reset()
            if moving:
                drivebase.settings(straight_speed=SPEED_LEVELS[level][0],
                                   turn_rate=SPEED_LEVELS[level][1])
                if direction in (1, 5):
                    # Point the way the robot pointed when this straight was
                    # recorded, so earlier turn errors don't bend the path.
                    await face_heading(start_heading + heading_start)
                    watch.reset()
                # Start each move from where the robot really is.
                drivebase.reset(0, r.hub.imu.heading())
            if direction in (1, 5):
                drivebase.straight(distance_mm, wait=False)
            elif direction in (3, 7):
                # Turn to the recorded absolute heading (not a relative amount).
                drivebase.turn(start_heading + heading_end - r.hub.imu.heading(), wait=False)
            else:
                r.stop_drive()

            if attachment_direction:
                left_attachement.run(ATTACHMENT_SPEED * attachment_direction)
            else:
                left_attachement.stop()

            # Same timing as the recording: each step (including pauses)
            # lasts at least as long as it did while recording.
            while not drivebase.done() or watch.time() < duration_ms:
                await wait(10)
            left_attachement.stop()
        print("Replay complete")
    finally:
        is_replaying = False
        r.stop_drive()
        left_attachement.stop()
        # Restore robot.py's normal speed/acceleration settings.
        drivebase.settings(*saved_settings)

async def main1():
    global is_recording, recording_sample
    global recording_left_start, recording_right_start, recording_heading_start
    global speed_level

    print_counter = 0
    active_direction = 0
    left_start = left.angle()
    right_start = right.angle()
    last_drive_value = None
    previous_y_pressed = False
    previous_a_pressed = False
    previous_x_pressed = False
    r.hub.display.char(str(speed_level + 1))
    print("Speed level {0} (press X to change)".format(speed_level + 1))
    while True:
        pressed = controller_pressed()
        y_pressed = Button.Y in pressed
        a_pressed = Button.A in pressed
        x_pressed = Button.X in pressed

        # X cycles the speed: 1 Slow -> 2 Normal -> 3 Fast -> 1 ...
        if x_pressed and not previous_x_pressed and not is_replaying:
            speed_level = (speed_level + 1) % len(SPEED_LEVELS)
            r.hub.display.char(str(speed_level + 1))
            print("Speed level {0}: drive {1:.0f} mm/s, turn {2} deg/s".format(
                speed_level + 1, SPEED_LEVELS[speed_level][0], SPEED_LEVELS[speed_level][1]))
        previous_x_pressed = x_pressed

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
                            recording_heading_start,
                        )
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
        direction = controller_dpad()
        if direction not in (1, 3, 5, 7):
            direction = 0
        if is_recording:
            attachment_direction = 0
            if Button.RB in pressed:
                attachment_direction = 1
            elif Button.LB in pressed:
                attachment_direction = -1
            # Encode direction, attachment and speed level in one number, so a
            # change in any of them starts a new recorded step.
            sample = direction + 8 * (attachment_direction + 1) + 24 * speed_level
            if recording_sample is None:
                recording_sample = sample
                recording_left_start = left.angle()
                recording_right_start = right.angle()
                recording_heading_start = r.hub.imu.heading()
                watch.reset()
            elif sample != recording_sample:
                elapsed = watch.time()
                append_recording_segment(
                    recording_sample,
                    elapsed,
                    recording_left_start,
                    recording_right_start,
                    recording_heading_start,
                )
                recording_sample = sample
                recording_left_start = left.angle()
                recording_right_start = right.angle()
                recording_heading_start = r.hub.imu.heading()
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
        # Use the direction pad for driving, at the selected speed level.
        drive_speed, turn_rate = SPEED_LEVELS[speed_level]
        if direction == 1:
            # Forward. Use the drive base so the gyro keeps us
            # driving straight.
            r.drive_straight(drive_speed)
        elif direction == 3:
            # Right
            r.drive_turn(turn_rate)
        elif direction == 5:
            # Reverse. Use the drive base so the gyro keeps us
            # driving straight.
            r.drive_straight(-drive_speed)
        elif direction == 7:
            # Left
            r.drive_turn(-turn_rate)
        else:
            # Nothing (or an ignored diagonal tap), so stop. Brake instead of
            # coasting so reversing direction doesn't have to wait for the
            # robot to roll to a stop.
            r.brake_drive()

async def attachment_stepper(motor, label, positive_button, negative_button):
    while True:
        if is_replaying:
            await wait(10)
            continue
        pressed = controller_pressed()
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
