# Screen Distance Monitor

A Python prototype for simulated eye-to-screen distance monitoring, with proximity alerts, a live distance chart, and CSV session export.

Inspired by a physics project, this prototype implements a distance-to-feedback workflow: read a distance, classify it, display an alert, and hide demo content when the distance falls below a threshold. All readings come from a slider or a predefined sequence. No physical sensor is connected, and no hardware experiments are claimed.

## Features

Simulate distances from 10 to 80 cm with a slider, sampled every 0.5 seconds. Classify readings as NORMAL above 30 cm, WARN from 25 to 30 cm inclusive, and BLOCK below 25 cm.
Optionally play a system bell when entering a warning or blocking state. Audibility depends on system settings.
Replace the application's demo content with a warning in BLOCK mode. This does not lock the computer or cover other applications.
Plot the latest 60 samples and export the current session as CSV.
Run a headless command-line demonstration without a desktop environment.

The 25 cm and 30 cm thresholds come from the source project's demonstration logic; they are not health standards validated by this project. The source's apparent typo, "25vm", is interpreted as 25 cm. A reading of exactly 25 cm produces WARN. Each sample is classified directly, without filtering or hysteresis, so readings fluctuating around a threshold may cause repeated state changes.

## Getting started

Requires Python 3.10 or later. The core logic and command-line demonstration use only the Python standard library; no pip packages are required.

On MacOS, open a terminal in the project folder and run:


python3 app.py


The desktop interface also requires Tkinter and a graphical display. Check Tkinter availability with `python3 -m tkinter`. If Tkinter is unavailable or you are working without a display, run the headless demonstration:


python3 app.py --demo


Run the tests from the project folder:


python3 -m unittest discover -s tests -v


On Windows, use `python` instead of `python3` if appropriate for your installation. The command-line demo overwrites `data/demo.csv`; use `--output other.csv` to select another path. CSV records are labeled as simulation data and use UTC timestamps.

## Demo walkthrough

1. Launch the application. The initial distance is 45 cm and the state is NORMAL.
2. Move the slider to 28 cm to trigger WARN. Enable the sound option if desired.
3. Move it to 20 cm. The demo content area displays CONTENT HIDDEN.
4. Return to 45 cm to restore the content.
5. Click **Export session CSV** to save the readings.

## Project structure

| File | Purpose |
| --- | --- |
| `monitor.py` | Distance classification, input validation, and ideal optical travel-time calculation |
| `app.py` | Desktop simulation, live chart, CSV export, and command-line demonstration |
| `tests/test_monitor.py` | Tests for threshold boundaries, invalid readings, and unit conversion |

## Physics background and limitations

The source project uses the ideal round-trip ranging equation `d = c × t / 2`. With its approximation `c = 3 × 10^8 m/s`, light takes 2 ns to travel to a target 30 cm away and return. A 40 kHz signal has a period of 25 microseconds. If this period were used directly as the timing resolution, each count would represent 3750 m of distance, making it unsuitable for centimeter-scale optical ranging.

A frequency of 40 kHz can describe modulation or pulse repetition, but it is not the optical frequency of infrared light. The interval between successive echoes also cannot simply be treated as the flight time from a single emission to its return. This prototype implements application logic and a separate ideal travel-time function; it does not implement a working infrared timing circuit.

A hardware integration could convert sensor readings to centimeters and pass them to `classify(distance_cm)`.

