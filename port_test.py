from pybricks.pupdevices import Motor
from pybricks.parameters import Port

for name, port in [("A", Port.A), ("B", Port.B), ("C", Port.C),
                    ("D", Port.D), ("E", Port.E), ("F", Port.F)]:
    try:
        m = Motor(port)
        print("Port {}: Motor OK".format(name))
    except Exception as e:
        print("Port {}: {}".format(name, e))
