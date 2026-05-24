# WARNING. This test program was AI generated. I was not going to spend a week to develop this application to see the accuracy of my program. Overall, its still a pretty cool program it generated. 

# input_timeline_tester.py
#
# pip install PySide6 pynput pyqtgraph
#
# High precision mouse/keyboard macro accuracy visualizer.
# Records:
#   - baseline inputs
#   - replay inputs
# Then compares timing drift between them.
#
# Features:
#   - global keyboard/mouse capture
#   - nanosecond timestamps
#   - zoomable timeline
#   - pan/drag
#   - timing error lines
#   - event table
#   - export/import json
#   - filter events
#
# Controls:
#   F8  -> toggle recording
#   ESC -> stop recording
#
# Workflow:
#   0. Start macro recorder
#   1. Click "Record baseline"
#   2. Perform inputs manually
#   3. Click "Stop baseline
#   4. Stop macro recorder
#   5. Start macro playback
#   6. Compare drift visually
#

import sys
import json
import math
import time
from dataclasses import dataclass, asdict
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QSplitter,
)

import pyqtgraph as pg

from pynput import keyboard, mouse


# ============================================================
# DATA
# ============================================================

@dataclass
class InputEvent:
    id: int
    kind: str
    time_ms: float

    key: Optional[str] = None
    button: Optional[str] = None

    x: Optional[int] = None
    y: Optional[int] = None

    dx: Optional[float] = None
    dy: Optional[float] = None


@dataclass
class MatchEvent:
    index: int
    label: str
    baseline: InputEvent
    replay: InputEvent
    error: float
    abs_error: float


# ============================================================
# APP
# ============================================================

class TimelineTester(QWidget):

    event_captured = Signal()
    stop_requested = Signal()  # Renamed to avoid recursive event loops

    def __init__(self):
        super().__init__()
        
        # FIX: Explicitly enforce QueuedConnection to safely pass data from background threads to the main UI thread
        self.event_captured.connect(self.render_plot, Qt.QueuedConnection)
        self.stop_requested.connect(self.stop_recording, Qt.QueuedConnection)
        
        self.setWindowTitle("Input Timeline Accuracy Tester")
        self.resize(1700, 950)

        self.event_id = 1

        self.capture_mode = "idle"

        self.current_events: List[InputEvent] = []

        self.baseline_events: List[InputEvent] = []
        self.replay_events: List[InputEvent] = []

        self.matches: List[MatchEvent] = []

        self.record_start_ns = 0

        self.zoom = 1.0

        self.keyboard_listener = None
        self.mouse_listener = None

        self.setup_ui()
        self.setup_plot()
        self.setup_hooks()

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        top = QHBoxLayout()

        self.record_btn = QPushButton("Record baseline")
        self.record_btn.clicked.connect(self.toggle_recording)

        self.compare_btn = QPushButton("Compare")
        self.compare_btn.clicked.connect(self.compare_sessions)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_all)

        self.export_btn = QPushButton("Export JSON")
        self.export_btn.clicked.connect(self.export_json)

        self.import_btn = QPushButton("Import JSON")
        self.import_btn.clicked.connect(self.import_json)

        self.status_label = QLabel("Idle")

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter events...")
        self.filter_input.textChanged.connect(self.render_everything)

        top.addWidget(self.record_btn)
        top.addWidget(self.compare_btn)
        top.addWidget(self.clear_btn)
        top.addWidget(self.export_btn)
        top.addWidget(self.import_btn)
        top.addWidget(self.filter_input)
        top.addWidget(self.status_label)

        layout.addLayout(top)

        splitter = QSplitter(Qt.Vertical)

        # timeline
        self.plot = pg.PlotWidget()

        splitter.addWidget(self.plot)

        # bottom section
        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)

        # table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "#",
            "Event",
            "Baseline",
            "Replay",
            "Error"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.cellClicked.connect(self.select_match)

        bottom_layout.addWidget(self.table, 3)

        # details
        right = QVBoxLayout()

        self.metrics = QLabel()
        self.metrics.setText("No comparison yet.")

        self.details = QTextEdit()
        self.details.setReadOnly(True)

        right.addWidget(self.metrics)
        right.addWidget(self.details)

        right_widget = QWidget()
        right_widget.setLayout(right)

        bottom_layout.addWidget(right_widget, 2)

        splitter.addWidget(bottom)

        layout.addWidget(splitter)

        self.setStyleSheet("""
            QWidget {
                background: #0b0f14;
                color: #e7eef7;
                font-size: 13px;
            }

            QPushButton {
                background: #1c2430;
                border: 1px solid #2d3c50;
                padding: 8px;
                border-radius: 6px;
            }

            QPushButton:hover {
                border: 1px solid #6ea8fe;
            }

            QLineEdit {
                background: #121923;
                border: 1px solid #2d3c50;
                padding: 6px;
                border-radius: 6px;
            }

            QTableWidget {
                background: #101720;
                gridline-color: #1f2c3d;
            }

            QTextEdit {
                background: #101720;
            }
        """)

    # ========================================================
    # PLOT
    # ========================================================

    def setup_plot(self):

        self.plot.setBackground("#0f1620")

        self.plot.showGrid(x=True, y=True, alpha=0.15)

        self.plot.setLabel("bottom", "Time", units="ms")

        self.plot.addLegend()

        self.plot.setMouseEnabled(x=True, y=False)

        self.plot.scene().sigMouseClicked.connect(
            self.timeline_clicked
        )

    # ========================================================
    # HOOKS
    # ========================================================

    def setup_hooks(self):

        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )

        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_scroll=self.on_scroll,
            on_move=self.on_move
        )

        self.keyboard_listener.start()
        self.mouse_listener.start()

    # ========================================================
    # RECORDING
    # ========================================================

    def now_ms(self):
        return (time.perf_counter_ns() - self.record_start_ns) / 1_000_000

    def toggle_recording(self):

        if self.capture_mode != "idle":
            self.stop_recording()
            return

        if not self.baseline_events:
            self.start_recording("baseline")
        else:
            self.start_recording("replay")

    def start_recording(self, mode):

        self.capture_mode = mode

        self.current_events = []

        self.record_start_ns = time.perf_counter_ns()

        self.record_btn.setText(f"Stop {mode}")

        self.status_label.setText(f"Recording {mode}...")

    def stop_recording(self):

        mode = self.capture_mode
        if mode == "idle":
            return

        if mode == "baseline":
            self.baseline_events = self.current_events.copy()

        elif mode == "replay":
            self.replay_events = self.current_events.copy()

        self.capture_mode = "idle"

        if self.baseline_events:
            self.record_btn.setText("Record replay")
        else:
            self.record_btn.setText("Record baseline")

        self.status_label.setText(
            f"Saved {mode}: {len(self.current_events)} events"
        )

        # FIX: Render immediately upon stopping instead of throwing a recursive signal trap
        self.render_everything()

    # ========================================================
    # INPUT HOOKS
    # ========================================================

    def capture_event(self, event: InputEvent):

        if self.capture_mode == "idle":
            return

        self.current_events.append(event)

        self.event_captured.emit()

    def next_id(self):

        i = self.event_id
        self.event_id += 1
        return i

    # keyboard

    def on_key_press(self, key):

        if key == keyboard.Key.esc:
            self.stop_requested.emit()  # FIX: Emit the safe stop signal
            return

        try:
            name = key.char
        except Exception:
            name = str(key)

        self.capture_event(
            InputEvent(
                id=self.next_id(),
                kind="keydown",
                key=name,
                time_ms=self.now_ms()
            )
        )

    def on_key_release(self, key):

        try:
            name = key.char
        except Exception:
            name = str(key)

        self.capture_event(
            InputEvent(
                id=self.next_id(),
                kind="keyup",
                key=name,
                time_ms=self.now_ms()
            )
        )

    # mouse

    def on_click(self, x, y, button, pressed):

        kind = "mousedown" if pressed else "mouseup"

        self.capture_event(
            InputEvent(
                id=self.next_id(),
                kind=kind,
                button=str(button),
                x=x,
                y=y,
                time_ms=self.now_ms()
            )
        )

    def on_scroll(self, x, y, dx, dy):

        self.capture_event(
            InputEvent(
                id=self.next_id(),
                kind="wheel",
                x=x,
                y=y,
                dx=dx,
                dy=dy,
                time_ms=self.now_ms()
            )
        )

    def on_move(self, x, y):

        # reduce noise
        return

    # ========================================================
    # COMPARISON
    # ========================================================

    def compare_sessions(self):

        if not self.baseline_events or not self.replay_events:

            QMessageBox.warning(
                self,
                "Missing data",
                "Need both baseline and replay recordings."
            )
            return

        self.matches.clear()

        count = min(
            len(self.baseline_events),
            len(self.replay_events)
        )

        for i in range(count):

            b = self.baseline_events[i]
            r = self.replay_events[i]

            err = r.time_ms - b.time_ms

            label = b.kind

            if b.key:
                label += ":" + b.key

            if b.button:
                label += ":" + b.button

            self.matches.append(
                MatchEvent(
                    index=i,
                    label=label,
                    baseline=b,
                    replay=r,
                    error=err,
                    abs_error=abs(err)
                )
            )

        self.render_everything()

    # ========================================================
    # RENDER
    # ========================================================

    def render_everything(self):

        self.render_plot()
        self.render_table()
        self.render_metrics()

    def passes_filter(self, text):

        f = self.filter_input.text().strip().lower()

        if not f:
            return True

        return f in text.lower()

    def render_plot(self):

        self.plot.clear()

        # Update counter label dynamically while user is inputting actions
        if self.capture_mode != "idle":
            self.status_label.setText(f"Recording {self.capture_mode}... ({len(self.current_events)} events)")

        # baseline data source selection (Show real-time updates if recording baseline)
        baseline_source = self.current_events if self.capture_mode == "baseline" else self.baseline_events
        bx = []
        by = []

        for e in baseline_source:

            label = e.kind + str(e.key or "") + str(e.button or "")

            if not self.passes_filter(label):
                continue

            bx.append(e.time_ms)
            by.append(2)

        self.plot.plot(
            bx,
            by,
            pen=None,
            symbol='o',
            symbolBrush="#5bd48f",
            name="Baseline"
        )

        # replay data source selection (Show real-time updates if recording replay)
        replay_source = self.current_events if self.capture_mode == "replay" else self.replay_events
        rx = []
        ry = []

        for e in replay_source:

            label = e.kind + str(e.key or "") + str(e.button or "")

            if not self.passes_filter(label):
                continue

            rx.append(e.time_ms)
            ry.append(1)

        self.plot.plot(
            rx,
            ry,
            pen=None,
            symbol='o',
            symbolBrush="#6ea8fe",
            name="Replay"
        )

        # error lines
        for m in self.matches:

            if not self.passes_filter(m.label):
                continue

            color = "#ff6b6b" if m.error >= 0 else "#5bd48f"

            line = pg.PlotCurveItem(
                x=[m.baseline.time_ms, m.replay.time_ms],
                y=[2, 1],  # Connect baseline (y=2) down to replay timeline (y=1)
                pen=pg.mkPen(color, width=2)
            )

            self.plot.addItem(line)

        self.plot.setYRange(-1, 4)

    def render_table(self):

        filtered = [
            m for m in self.matches
            if self.passes_filter(m.label)
        ]

        self.table.setRowCount(len(filtered))

        for row, m in enumerate(filtered):

            values = [
                str(row + 1),
                m.label,
                f"{m.baseline.time_ms:.3f}",
                f"{m.replay.time_ms:.3f}",
                f"{m.error:+.3f} ms"
            ]

            for col, val in enumerate(values):

                item = QTableWidgetItem(val)

                if col == 4:

                    if m.error >= 0:
                        item.setForeground(QColor("#ff6b6b"))
                    else:
                        item.setForeground(QColor("#5bd48f"))

                self.table.setItem(row, col, item)

    def render_metrics(self):

        if not self.matches:

            self.metrics.setText("No comparison data.")
            return

        mean_abs = sum(
            m.abs_error for m in self.matches
        ) / len(self.matches)

        max_abs = max(
            m.abs_error for m in self.matches
        )

        bias = sum(
            m.error for m in self.matches
        ) / len(self.matches)

        self.metrics.setText(
            f"""
Matched Events: {len(self.matches)}

Mean Absolute Error:
{mean_abs:.3f} ms

Max Error:
{max_abs:.3f} ms

Bias:
{bias:+.3f} ms
"""
        )

    # ========================================================
    # DETAILS
    # ========================================================

    def select_match(self, row, column):

        filtered = [
            m for m in self.matches
            if self.passes_filter(m.label)
        ]

        if row >= len(filtered):
            return

        m = filtered[row]

        self.details.setText(
            f"""
Event:
{m.label}

Baseline:
{m.baseline.time_ms:.6f} ms

Replay:
{m.replay.time_ms:.6f} ms

Error:
{m.error:+.6f} ms

Absolute Error:
{m.abs_error:.6f} ms
"""
        )

    def timeline_clicked(self, event):

        pass

    # ========================================================
    # FILES
    # ========================================================

    def export_json(self):

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export JSON",
            "input_timeline.json",
            "JSON (*.json)"
        )

        if not path:
            return

        data = {
            "baseline": [
                asdict(e)
                for e in self.baseline_events
            ],
            "replay": [
                asdict(e)
                for e in self.replay_events
            ]
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def import_json(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import JSON",
            "",
            "JSON (*.json)"
        )

        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.baseline_events = [
            InputEvent(**e)
            for e in data.get("baseline", [])
        ]

        self.replay_events = [
            InputEvent(**e)
            for e in data.get("replay", [])
        ]

        self.compare_sessions()

    # ========================================================
    # CLEAR
    # ========================================================

    def clear_all(self):

        self.capture_mode = "idle"

        self.current_events.clear()
        self.baseline_events.clear()
        self.replay_events.clear()
        self.matches.clear()

        self.record_btn.setText("Record baseline")

        self.status_label.setText("Idle")

        self.details.clear()

        self.render_everything()


# ============================================================
# MAIN
# ============================================================

def main():

    app = QApplication(sys.argv)

    pg.setConfigOptions(antialias=True)

    w = TimelineTester()
    w.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()