"""Run a desktop simulation, or a deterministic headless demo."""
import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
from monitor import classify, light_round_trip_seconds

FIELDS = ['timestamp_utc', 'source', 'distance_cm', 'state']


def log_row(writer, reading):
    writer.writerow([datetime.now(timezone.utc).isoformat(), 'simulation',
                     f'{reading.distance_cm:.1f}', reading.state])


def demo(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(FIELDS)
        for cm in [50, 40, 31, 30, 27, 25, 24, 20, 26, 35, 50]:
            reading = classify(cm)
            log_row(writer, reading)
            print(f'{cm:5.1f} cm  {reading.state}')
    print(f'Saved: {path}')


def gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.title('Screen Distance Monitor | Simulation')
    root.geometry('820x640')
    root.minsize(700, 610)
    root.configure(bg='#101827')
    samples = []
    previous_state = None
    distance = tk.DoubleVar(value=45)
    sound = tk.BooleanVar(value=False)

    def label(text, size, color='#e5edf8'):
        widget = tk.Label(root, text=text, bg='#101827', fg=color,
                          font=('Helvetica', size))
        widget.pack(pady=6)
        return widget

    label('SCREEN DISTANCE MONITOR', 22)
    label('SIMULATED DATA  /  No sensor connected', 11, '#94a3b8')
    metric = label('45.0 cm', 36)
    status = label('NORMAL', 18)
    label('Move the slider to simulate the eye-to-screen distance.', 12)
    tk.Scale(root, from_=10, to=80, resolution=0.5, orient='horizontal',
             variable=distance, length=560, bg='#101827', fg='#e5edf8',
             highlightthickness=0).pack(pady=6)
    tk.Checkbutton(root, text='Sound on warning entry (system bell)',
                   variable=sound, bg='#101827', fg='#e5edf8',
                   selectcolor='#243047', activebackground='#101827').pack()
    panel = tk.Label(root, text='', font=('Helvetica', 15), height=3,
                     bg='#1d3441', fg='white', wraplength=620)
    panel.pack(fill='x', padx=38, pady=12)
    chart = tk.Canvas(root, height=120, bg='#172235', highlightthickness=0)
    chart.pack(fill='x', padx=38)
    label('Last 60 samples · one sample every 0.5 seconds · 10–80 cm', 10, '#94a3b8')

    def export():
        filename = filedialog.asksaveasfilename(defaultextension='.csv',
                   initialfile='distance-session.csv', filetypes=[('CSV', '*.csv')])
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(FIELDS)
                    writer.writerows(samples)
            except OSError as exc:
                messagebox.showerror('Export failed', str(exc))
            else:
                messagebox.showinfo('Export complete', f'Saved {len(samples)} samples.')

    tk.Button(root, text='Export session CSV', command=export).pack(pady=5)

    def tick():
        nonlocal previous_state
        reading = classify(distance.get())
        colors = {'NORMAL': '#5ee0b5', 'WARN': '#fbbf24', 'BLOCK': '#fb7185'}
        messages = {'NORMAL': 'Demo content is visible.',
                    'WARN': 'Distance is 30 cm or less. Move farther away.',
                    'BLOCK': 'CONTENT HIDDEN\nDistance is below 25 cm. Move farther away.'}
        metric.config(text=f'{reading.distance_cm:.1f} cm')
        status.config(text=reading.state, fg=colors[reading.state])
        panel.config(text=messages[reading.state],
                     bg='#672b3c' if reading.state == 'BLOCK' else '#1d3441')
        if sound.get() and reading.state != 'NORMAL' and reading.state != previous_state:
            root.bell()
        previous_state = reading.state
        samples.append([datetime.now(timezone.utc).isoformat(), 'simulation',
                        f'{reading.distance_cm:.1f}', reading.state])
        chart.delete('all')
        width = max(chart.winfo_width(), 600)
        y = lambda cm: 110 - (cm - 10) / 70 * 100
        for threshold in (25, 30):
            chart.create_line(0, y(threshold), width, y(threshold), fill='#64748b', dash=(4, 4))
            chart.create_text(width-25, y(threshold)-8, text=str(threshold), fill='#cbd5e1')
        points = []
        for i, row in enumerate(samples[-60:]):
            points.extend([i * (width-60) / 59 + 8, y(float(row[2]))])
        if len(points) >= 4:
            chart.create_line(*points, fill='#5ee0b5', width=2)
        root.after(500, tick)

    tick()
    root.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true', help='Run without a desktop window')
    parser.add_argument('--output', type=Path, default=Path('data/demo.csv'),
                        help='CSV output for --demo (overwrites the selected file)')
    args = parser.parse_args()
    if args.demo:
        demo(args.output)
        print(f'30 cm ideal optical round-trip: {light_round_trip_seconds(30)*1e9:.1f} ns')
    else:
        gui()
