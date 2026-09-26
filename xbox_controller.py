import umath

from pybricks.iodevices import XboxController
from pybricks.parameters import Button, Direction, Port, Stop
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import multitask, run_task, wait

# Wheel size, used to convert motor angle to distance driven.
WHEEL_DIAMETER = 55.5  # mm

# Distance between the centers of the left and right wheels, used to
# convert wheel angle to the angle the robot itself turned during a
# pivot turn, and by the drive base for gyro-corrected driving.
TRACK_WIDTH = 80  # mm

# Set up all devices.
left = Motor(Port.C, Direction.COUNTERCLOCKWISE)
right = Motor(Port.D, Direction.CLOCKWISE)
left_attachement = Motor(Port.F, Direction.CLOCKWISE)
right_attachement = Motor(Port.E, Direction.CLOCKWISE)
controller = XboxController()

# Treat wherever the attachements happen to be at startup as 0, so
# their angle is relative to the start of the program rather than
# whatever the motor's absolute encoder reads.
left_attachement.reset_angle(0)
right_attachement.reset_angle(0)

# A high acceleration limit lets the controller apply torque quickly
# for a step, instead of ramping up gently and possibly not
# developing enough force to overcome friction within just 5 degrees.
left_attachement.control.limits(acceleration=5000)
right_attachement.control.limits(acceleration=5000)

# Used for forward/reverse driving, so the gyro can keep us driving
# straight. Left/right pivot turns and diagonal turns still drive the
# left/right motors directly, which automatically cancels the drive
# base's current maneuver.
drivebase = DriveBase(left, right, WHEEL_DIAMETER, TRACK_WIDTH)
drivebase.use_gyro(True)

# Linear speed for forward/reverse that matches the previous 250 deg/s
# wheel speed used for turning.
DRIVE_SPEED = 250 / 360 * umath.pi * WHEEL_DIAMETER  # mm/s

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

# Movement recording storage
movement_log = []
recording_enabled = True  # Always recording

async def main1():
    # This main task will handle driving and the motors that power
    # the left and right attachements.
    left.control.limits(acceleration=2500)
    right.control.limits(acceleration=2500)
    print_counter = 0
    active_direction = 0
    left_start = left.angle()
    right_start = right.angle()
    last_drive_value = None
    playback_in_progress = False
    while True:
        await wait(1)
        pressed = controller.buttons.pressed()

        # Check if Y button is pressed to start playback
        if Button.Y in pressed and not playback_in_progress:
            playback_in_progress = True
            print("\n>>> Playback triggered! <<<")
            await playback_movements()
            playback_in_progress = False
            # Reset tracking variables after playback
            active_direction = 0
            left_start = left.angle()
            right_start = right.angle()
            last_drive_value = None
            continue
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
            # Record the direction change
            if recording_enabled:
                movement = {
                    "type": "drive_start",
                    "direction": direction,
                    "direction_name": DIRECTION_NAMES[direction]
                }
                movement_log.append(movement)
                print("[RECORDED] Drive: {0}".format(DIRECTION_NAMES[direction]))
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
                        # Record the angle turned
                        if recording_enabled:
                            movement = {
                                "type": "turn",
                                "direction": active_direction,
                                "angle_deg": drive_value
                            }
                            movement_log.append(movement)
                            print("[RECORDED] Turn angle: {0:.1f} deg".format(drive_value))
                else:
                    average_angle = (left_delta + right_delta) / 2
                    drive_value = round(average_angle / 360 * umath.pi * WHEEL_DIAMETER / 10, 1)
                    if drive_value != last_drive_value:
                        last_drive_value = drive_value
                        print("Distance driven: {0:.1f} cm".format(drive_value))
                        # Record the distance driven
                        if recording_enabled:
                            movement = {
                                "type": "drive",
                                "direction": active_direction,
                                "distance_cm": drive_value
                            }
                            movement_log.append(movement)
                            print("[RECORDED] Distance: {0:.1f} cm".format(drive_value))
        # Use the direction pad for driving.
        if direction == 1:
            # Forward. Use the drive base so the gyro keeps us
            # driving straight.
            drivebase.drive(DRIVE_SPEED, 0)
        elif direction == 3:
            # Right
            left.run(50)
            right.run(-50)
        elif direction == 5:
            # Reverse. Use the drive base so the gyro keeps us
            # driving straight.
            drivebase.drive(-DRIVE_SPEED, 0)
        elif direction == 7:
            # Left
            left.run(-50)
            right.run(50)
        else:
            # Nothing (or an ignored diagonal tap), so stop.
            drivebase.stop()

async def attachment_stepper(motor, label, positive_button, negative_button):
    # While the button is held, step the motor 5 degrees, pause
    # 100 ms, and repeat until it's released. A quick tap results in
    # a single 5 degree step.
    #
    # We track the intended position ourselves and always command an
    # absolute run_target(), rather than a relative run_angle() from
    # wherever the motor actually ended up. That way, if a step
    # under- or overshoots (e.g. from friction in the mechanism), the
    # next tap corrects back to the exact intended multiple of 5
    # instead of compounding the error onto every step after it.
    target = motor.angle()
    while True:
        pressed = controller.buttons.pressed()
        if positive_button in pressed:
            target += 5
            await step_to_target(motor, target)
            actual_angle = motor.angle()
            print("{0} angle: {1} deg".format(label, actual_angle))
            # Record the attachment movement
            if recording_enabled:
                movement = {
                    "type": "attachment",
                    "attachment": label,
                    "button": str(positive_button),
                    "angle_deg": actual_angle,
                    "delta": +5
                }
                movement_log.append(movement)
                print("[RECORDED] {0}: {1} deg (+5)".format(label, actual_angle))
            await wait(100)
        elif negative_button in pressed:
            target -= 5
            await step_to_target(motor, target)
            actual_angle = motor.angle()
            print("{0} angle: {1} deg".format(label, actual_angle))
            # Record the attachment movement
            if recording_enabled:
                movement = {
                    "type": "attachment",
                    "attachment": label,
                    "button": str(negative_button),
                    "angle_deg": actual_angle,
                    "delta": -5
                }
                movement_log.append(movement)
                print("[RECORDED] {0}: {1} deg (-5)".format(label, actual_angle))
            await wait(100)
        else:
            await wait(1)

async def step_to_target(motor, target):
    # run_target()'s wait=True returns once the planned trajectory
    # time elapses, but under Stop.HOLD the motor keeps actively
    # correcting afterward. Rather than guess how long that takes,
    # actively wait (up to 500 ms) until it has actually arrived,
    # so the angle we print/act on next is the real, settled value.
    await motor.run_target(300, target, Stop.HOLD, wait=True)
    for _ in range(50):
        if abs(motor.angle() - target) <= 1:
            return
        await wait(10)

def print_movement_summary():
    # Print a summary of all recorded movements
    print("\n=== MOVEMENT LOG SUMMARY ===")
    print("Total movements recorded: {0}".format(len(movement_log)))
    if len(movement_log) > 0:
        print("\nMovements:")
        for i, move in enumerate(movement_log):
            if move["type"] == "drive_start":
                print("{0}: START - {1}".format(i+1, move["direction_name"]))
            elif move["type"] == "drive":
                print("{0}: DRIVE - {1} cm".format(i+1, move["distance_cm"]))
            elif move["type"] == "turn":
                print("{0}: TURN - {1} deg".format(i+1, move["angle_deg"]))
            elif move["type"] == "attachment":
                print("{0}: {1} - {2} deg ({3:+d})".format(
                    i+1, move["attachment"], move["angle_deg"], move["delta"]))
    print("=== END LOG ===\n")

async def playback_movements():
    # Playback all recorded movements
    global recording_enabled

    if len(movement_log) == 0:
        print("No movements to playback!")
        return

    # Temporarily disable recording during playback
    was_recording = recording_enabled
    recording_enabled = False

    print("\n=== STARTING PLAYBACK ===")
    print("Playing back {0} movements...".format(len(movement_log)))

    for i, move in enumerate(movement_log):
        print("[PLAYBACK {0}/{1}] ".format(i+1, len(movement_log)), end="")

        if move["type"] == "drive_start":
            # Starting a new direction - just print it
            print("Starting: {0}".format(move["direction_name"]))

        elif move["type"] == "drive":
            # Drive forward or reverse a certain distance
            distance_cm = move["distance_cm"]
            direction = move["direction"]
            print("Driving {0} cm".format(distance_cm))

            # Convert cm to motor degrees
            distance_mm = distance_cm * 10
            motor_degrees = distance_mm / (umath.pi * WHEEL_DIAMETER) * 360

            # Reset motor starting positions
            left_start = left.angle()
            right_start = right.angle()

            # Drive forward (1) or reverse (5)
            if direction == 1:
                drivebase.drive(DRIVE_SPEED, 0)
            elif direction == 5:
                drivebase.drive(-DRIVE_SPEED, 0)

            # Wait until we've driven the target distance
            while True:
                left_delta = abs(left.angle() - left_start)
                right_delta = abs(right.angle() - right_start)
                average_delta = (left_delta + right_delta) / 2
                if average_delta >= abs(motor_degrees):
                    drivebase.stop()
                    break
                await wait(10)

        elif move["type"] == "turn":
            # Turn left or right a certain angle
            angle_deg = move["angle_deg"]
            direction = move["direction"]
            print("Turning {0} deg".format(angle_deg))

            # Convert robot turn angle to wheel angle
            wheel_angle = angle_deg * TRACK_WIDTH / WHEEL_DIAMETER

            # Reset motor starting positions
            left_start = left.angle()
            right_start = right.angle()

            # Turn right (3) or left (7)
            if direction == 3:
                left.run(50)
                right.run(-50)
            elif direction == 7:
                left.run(-50)
                right.run(50)

            # Wait until we've turned the target angle
            while True:
                left_delta = left.angle() - left_start
                right_delta = right.angle() - right_start
                turned_angle = abs(left_delta - right_delta) / 2
                if turned_angle >= wheel_angle:
                    left.stop()
                    right.stop()
                    break
                await wait(10)

        elif move["type"] == "attachment":
            # Move an attachment to a specific angle
            attachment_name = move["attachment"]
            target_angle = move["angle_deg"]
            print("{0} to {1} deg".format(attachment_name, target_angle))

            # Determine which motor to use
            if "Left" in attachment_name:
                motor = left_attachement
            else:
                motor = right_attachement

            # Move to the target angle
            await motor.run_target(300, target_angle, Stop.HOLD, wait=True)
            await wait(100)

        # Small pause between movements
        await wait(200)

    print("=== PLAYBACK COMPLETE ===\n")

    # Re-enable recording
    recording_enabled = was_recording

async def main():
    await multitask(
        main1(),
        attachment_stepper(left_attachement, "Left attachement", Button.RB, Button.LB),
        attachment_stepper(right_attachement, "Right attachement", Button.X, Button.B),
    )

run_task(main())
