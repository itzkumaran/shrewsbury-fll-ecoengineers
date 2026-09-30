################################################################
# check_ports.py
#
# Diagnostic tool: lists which motor or sensor the hub detects
# on each port (A-F). Use it when you get an ENODEV error
# ("A sensor or motor is not connected to the specified port")
# to compare what is plugged in with PORT_MAPPING in robot.py.
#
# Run: scripts/run-hub.sh "Lucky Chicken" check_ports.py
#
# Dependencies:
# - pybricks.iodevices (PUPDevice)
# - pybricks.parameters (Port)
#
################################################################

from pybricks.iodevices import PUPDevice
from pybricks.parameters import Port

PORTS = {
    "A": Port.A,
    "B": Port.B,
    "C": Port.C,
    "D": Port.D,
    "E": Port.E,
    "F": Port.F,
}

# LEGO Powered Up device type IDs
DEVICE_NAMES = {
    1: "Wedo 2.0 Medium Motor",
    2: "Powered Up Train Motor",
    8: "Powered Up Light",
    34: "Wedo 2.0 Tilt Sensor",
    35: "Wedo 2.0 Motion Sensor",
    37: "BOOST Color Distance Sensor",
    38: "BOOST Interactive Motor",
    46: "Technic Large Motor",
    47: "Technic XL Motor",
    48: "SPIKE Medium Angular Motor",
    49: "SPIKE Large Angular Motor",
    61: "SPIKE Color Sensor",
    62: "SPIKE Ultrasonic Sensor",
    63: "SPIKE Force Sensor",
    64: "SPIKE 3x3 Color Light Matrix",
    65: "SPIKE Small Angular Motor",
    75: "Technic Medium Angular Motor",
    76: "Technic Large Angular Motor",
}


def check_ports():
    print("Port check:")
    for letter, port in PORTS.items():
        try:
            device_id = PUPDevice(port).info()["id"]
            name = DEVICE_NAMES.get(device_id, "Unknown device")
            print("  Port", letter, "->", name, "(id", str(device_id) + ")")
        except OSError:
            print("  Port", letter, "-> nothing detected")


if __name__ == "__main__":
    check_ports()
