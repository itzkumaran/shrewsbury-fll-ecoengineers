# Changelog

## 2026-09-28

### Added
- Added Xbox controls for both attachment motors: RB/LB operate the left motor, and X/B operate the right motor.
- Added recording and playback support for both attachment motors.
- Added LT trigger control to run `recorded_mission.py` from the Xbox controller.

### Fixed
- Changed recorded mission execution to use cooperative waits so attachment commands continue running while the mission waits.
- Replaced generated fixed-duration waits with completion checks for the drive base and both attachment motors.
- Added `done()` to the robot motor interface and made absent attachment motors report completion.
- Resolved the Pylance warning on the Pybricks PID getter while preserving the heading-gain adjustment.
- Configured VS Code to discover the project virtual environment using a platform-neutral path; installed the Pybricks development packages in the local environment.