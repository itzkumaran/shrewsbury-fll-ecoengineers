# Robot Experiments: How We Fixed lucky-chicken-2

This is the story of how we made our robot drive straight and turn accurately. We used the **scientific method**: notice a problem, guess why, test the guess, fix it, and test again.

You can run the same tests yourself with `robot_check.py` (see the end of this page).

---

## What the robot can measure about itself

Our robot has two built-in "senses" we used as evidence:

| Sensor | What it measures | Like... |
|---|---|---|
| **Motor encoders** | How many degrees each wheel turned | Counting your steps |
| **Gyro** (inside the hub) | Which way the robot is facing | A compass |

The encoders tell us how far the **wheels** turned. The gyro tells us which way the **robot** is really pointing. When those two disagree, something is wrong.

---

## Experiment 1: Which ports have motors?

**Problem:** The robot showed *"A sensor or motor is not connected to the specified port."*

**Test:** We ran `port_test.py`, which tries every port (A–F) and reports what it finds.

**Result:**

| Port | Found |
|---|---|
| A | Motor ✅ |
| B | Motor ✅ |
| C | Empty |
| D | Empty |
| E | Motor ✅ |
| F | Motor ✅ |

Then we spun each motor by itself. B and F turned the robot (they're the **drive wheels**). A and E did not (they're the **attachment motors**).

**Fix:** We told `robot.py` exactly which motor is on which port.

---

## Experiment 2: The "Invalid argument" error

**Problem:** When the robot started, it quietly printed *"Drive base initialization error: Invalid argument."*

**Test:** We tried different acceleration numbers one at a time.

| Acceleration | Result |
|---|---|
| 10000 | ❌ Error |
| 1000 | ✅ Works |
| 500 | ✅ Works |
| 100 | ✅ Works |

**Fix:** 10000 was too big for the robot's software. We lowered it.

**Lesson:** An error message that gets "caught" and hidden can still break things. Always read the startup messages.

---

## Experiment 3: Forward was backward!

**Problem:** When we told the robot to drive forward, it drove **backward**. When we told it to turn right, it turned **left**.

**Evidence:** The encoders said the robot turned **+91°** but the gyro said **−91°**. Same size, opposite sign. That means the robot's idea of "left and right" was flipped.

**Fix:** Both drive motors were set to spin the wrong way. We flipped both of them in `robot.py`.

**After the fix:**

| Command | Result |
|---|---|
| Drive forward 100 mm | Drove forward ✅ |
| Turn right 90° | Encoder +91°, gyro +90° ✅ (signs match now) |

**Lesson:** When two sensors disagree, one of your settings is probably wrong.

---

## Experiment 4: Turns went too far

**Problem:** When we asked for a 360° spin (one full circle), the gyro measured **414°**. That's about 15% too far.

**Why:** To turn, the robot needs to know the distance between its two wheels (the **axle track**). We had it set to **130 mm**.

**Math:** If the robot turns too far, it thinks its wheels are farther apart than they really are.

```
real axle track = 130 × (360 ÷ 414) ≈ 113 mm
```

**Check:** You measured the real robot with a ruler: **112 mm**. Our math was only 1 mm off! ✅

**After the fix:**

| Command | Gyro measured |
|---|---|
| Turn 90° | 90.7° |
| Turn 360° | 360.0° |

---

## Experiment 5: Does it drive the right distance?

**Test:** We drove forward 300 mm and measured with a ruler.

**Result:** Robot said 299 mm. Ruler said about 300 mm. ✅

**Why it's correct:** The 56 mm wheel size (printed on the tire) and the 112 mm axle track both match the robot's own measurements, so no change was needed.

---

## Experiment 6: The drift problem

**Problem:** We drove forward 300 mm and back 300 mm, **5 times in a row**. The robot should end where it started, but it ended up **42 mm to the right**.

**Clue:** It only drifted on the **forward** trips, not the backward ones.

**Our guess (hypothesis):** Our robot has 2 drive wheels in the back and **1 ball in the front**. When driving forward, the ball is being **pushed**. When driving backward, it is being **pulled**. Think of a shopping cart: pushing it makes it wander, pulling it keeps it straight. Any friction on the ball steers the front a little.

**Is the robot level?** The gyro said it leans less than 1° side to side, so tilting is not the cause.

**Fix, part 1:** We turned on **gyro steering**. Now the robot checks its "compass" while driving and corrects itself.

**Fix, part 2:** We made the steering correction stronger and made starts and stops gentler.

**Results (you measured with a ruler each time):**

| Try | Settings | Drift after 5 trips |
|---|---|---|
| 1 | No gyro steering | 42 mm |
| 2 | Gyro steering ×2, gentler start | 20 mm |
| 3 | Gyro steering ×4 | 9 mm |
| 4 | Gyro steering ×8 | **3 mm** ✅ |

That's **93% less drift!** Over 3 meters of driving, the robot is now only off by about the width of a pencil.

**Lesson:** Change **one thing at a time** and measure each time. That's how you know which change actually helped.

---

## Experiment 7: Fixing record and replay

**Problem:** The Xbox controller can **record** a path you drive and **replay** it. But the replay did not follow the path you drove.

**Clue 1:** After turning, when you drove forward or backward, the robot **turned back** toward its old direction by itself.

**Test:** Turn right 45°, then back up, and watch the gyro.

| Version | Robot turned while backing up |
|---|---|
| Old code | −46° (it undid the whole turn!) |
| Fixed code | 0.2° ✅ |

**Why:** Every time you started driving, the code "reset" the robot's direction to zero. With gyro steering on, the robot then tried to point back to its *old* zero direction.

**Clue 2:** When you let go of the D-pad, the robot keeps rolling a few millimeters, about 6 mm. The recording saved that roll as part of the "stop", and replay ignored it, so every move came up short.

**Fixes:**
- Don't reset the direction when starting to drive.
- Add the rolling-after-release to the move before it.
- Measure turns with the **gyro** instead of guessing from the wheels.
- Before each replayed move, start from where the robot really is.
- Make the printed mission code complete, so it can be pasted into a mission file.

**Result:** You drove a path with 17 moves using the Xbox controller, then replayed it:

| Moves | Worst difference |
|---|---|
| 9 straight drives | 1.3 mm (on a 562 mm drive!) |
| 8 turns | 1.8° |

**Lesson:** If one part of the code (the reset) fights another part (the gyro), the robot does something nobody asked for. Test each piece by itself to find which one is the problem.

---

## Final robot settings

| Setting | Value | Why |
|---|---|---|
| Left drive motor | Port B | Found by the port test |
| Right drive motor | Port F | Found by the port test |
| Attachment motors | Ports A and E | Found by the port test |
| Wheel size | 56 mm | Printed on the tire |
| Wheels | 56 x 28 mm black | Wider tires grip better: almost no slipping on turns |
| Axle track | 114 mm | We tested 104 to 119 mm; at 114 the wheels' turn count matches the gyro. A ruler says 119 mm, but wide tires turn as if the wheels were a bit closer together (blue 56 x 14 wheels need 113 mm) |
| Gyro steering | On, strength ×8 | Cut drift from 42 mm to 3 mm |

**Remember:** `straight(+)` = forward, `turn(+)` = right.

**Important:** After you start a program, **don't touch the robot for 1 second**. The gyro is getting ready.

---

## Run the tests yourself: `robot_check.py`

1. Put the robot on the floor with **50 cm of space** in front and behind.
2. Put tape next to a wheel to mark the **start**.
3. Run it (change the robot name if needed):

   ```bash
   python -m pybricksdev run ble --name lucky-chicken-2 robot_check.py
   ```

4. **Don't touch the robot** while it runs (about 1 minute).
5. Read the results. `PASS` means good. `CHECK` means look closer.

Example output from lucky-chicken-2:

```
PASS     1. Gyro is steady            moved +0.03 deg while sitting still
PASS     2. Drives 300 mm straight    drove 299 mm, turned +0.1 deg
PASS     3. Turn RIGHT 90             gyro says +90.9 deg (right is +)
PASS     4. Turn LEFT 90              gyro says -91.3 deg (left is -)
PASS     5. Drift after 5 trips       about +0.7 mm sideways (+ = right), facing +0.3 deg
```

6. Measure how far the robot ended up from your tape. Real drift is usually a bit more than the number shown, because the gyro can't feel the wheels sliding sideways.

### If a test says CHECK

| Test | What to try |
|---|---|
| 1. Gyro steady | Make sure nobody touched the robot. Put it on a flat, still surface. |
| 2. Drives straight | Check tires aren't loose. Check the front ball spins freely. |
| 3–4. Turns | Wrong direction? The motor directions need fixing. Wrong amount? Adjust the axle track. |
| 5. Drift | Clean the front ball and make sure it's centered between the wheels. |

For the technical details, see [pybricks_setup_for_vscode.md](pybricks_setup_for_vscode.md) section 14.
