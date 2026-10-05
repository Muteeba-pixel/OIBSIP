"""
chart.py
========
Matplotlib visualization module for the Advanced BMI Calculator & Health Tracker.

Generates sleek, modern trend line charts showing a user's BMI trajectory over
time, complete with WHO reference health bands, data point callouts, and clean styling.

OASIS Infobyte Python Programming Internship - Task 2
Author: OASIS Intern / Python Developer
"""

from typing import Any, Dict, List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta


# Color constants matching the modern dashboard palette
THEME = {
    "bg": "#0f172a",          # Deep slate background
    "card_bg": "#1e293b",     # Slightly lighter slate for figure face
    "text": "#f8fafc",        # Bright readable text
    "muted_text": "#94a3b8",  # Muted secondary text
    "grid": "#334155",        # Subtle gridlines
    "line": "#38bdf8",        # Vibrant cyan trendline
    "marker": "#0284c7",      # Marker fill
    "band_under": "#38bdf8",  # Underweight accent
    "band_normal": "#10b981", # Normal weight accent (emerald)
    "band_over": "#f59e0b",   # Overweight accent (amber)
    "band_obese": "#ef4444",  # Obese accent (crimson)
}


def render_bmi_chart(figure: Figure, records: List[Dict[str, Any]], user_name: str) -> None:
    """
    Render or update the BMI trend chart onto an existing Matplotlib Figure.

    Args:
        figure: Matplotlib Figure instance (e.g. embedded inside Tkinter Canvas).
        records: List of record dictionaries sorted chronologically (oldest to newest).
        user_name: Selected user's name for chart header.
    """
    figure.clear()
    ax = figure.add_subplot(111)

    # Set background colors
    figure.patch.set_facecolor(THEME["card_bg"])
    ax.set_facecolor(THEME["bg"])

    # If no records exist, render an informative empty state
    if not records:
        ax.text(
            0.5, 0.5,
            f"No historical records found for '{user_name}'.\n\nCalculate and click 'Save Record' to start tracking your BMI trend!",
            color=THEME["muted_text"],
            fontsize=12,
            ha="center",
            va="center",
            transform=ax.transAxes,
            wrap=True
        )
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(THEME["grid"])
        figure.tight_layout(pad=1.5)
        return

    # Parse timestamps and BMI values from actual database records
    dates = []
    bmis = []

    for r in records:
        raw_date = r["created_at"]
        try:
            dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                dt = datetime.strptime(raw_date, "%Y-%m-%d")
            except ValueError:
                dt = datetime.now()
        dates.append(dt)
        bmis.append(float(r["bmi"]))

    # Determine Y-axis limits dynamically with margin
    min_val = min(bmis)
    max_val = max(bmis)
    y_min = max(10.0, min(14.0, min_val - 3.0))
    y_max = max(36.0, max_val + 3.0)
    ax.set_ylim(y_min, y_max)

    # Draw WHO Reference Colored Background Bands
    # Underweight: < 18.5
    ax.axhspan(y_min, 18.5, color=THEME["band_under"], alpha=0.12, label="Underweight (< 18.5)")
    # Normal: 18.5 - 24.9
    ax.axhspan(18.5, 24.9, color=THEME["band_normal"], alpha=0.18, label="Normal (18.5 - 24.9)")
    # Overweight: 25.0 - 29.9
    ax.axhspan(24.9, 29.9, color=THEME["band_over"], alpha=0.12, label="Overweight (25.0 - 29.9)")
    # Obese: >= 30.0
    ax.axhspan(29.9, y_max, color=THEME["band_obese"], alpha=0.12, label="Obese (≥ 30.0)")

    # Plot Reference Threshold Lines
    for threshold, col in [(18.5, THEME["band_under"]), (24.9, THEME["band_normal"]), (29.9, THEME["band_over"])]:
        ax.axhline(threshold, color=col, linestyle="--", linewidth=0.9, alpha=0.6)

    # Plot Trend Line and Data Points
    if len(dates) == 1:
        # Single point view: center with comfortable time margin
        ax.scatter(dates, bmis, color=THEME["line"], s=120, zorder=5, edgecolor="#ffffff", linewidth=1.8)
        ax.annotate(
            f"BMI {bmis[0]:.2f}\n({records[0]['category']})\n{dates[0].strftime('%Y-%m-%d %H:%M')}",
            xy=(dates[0], bmis[0]),
            xytext=(0, 20),
            textcoords="offset points",
            ha="center",
            fontsize=9.5,
            fontweight="bold",
            color=THEME["text"],
            bbox=dict(boxstyle="round,pad=0.4", fc=THEME["card_bg"], ec=THEME["line"], lw=1.2)
        )
        margin = timedelta(days=1)
        ax.set_xlim(dates[0] - margin, dates[0] + margin)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d, %Y\n%H:%M"))
    else:
        # Multiple points: line plot with markers and breathing room
        ax.plot(
            dates, bmis,
            color=THEME["line"],
            linewidth=2.5,
            marker="o",
            markersize=7,
            markerfacecolor=THEME["text"],
            markeredgecolor=THEME["line"],
            markeredgewidth=2,
            zorder=4,
            label="BMI Trajectory"
        )
        ax.margins(x=0.08)

        # Annotations: show values clearly on points
        if len(dates) <= 8:
            # Annotate all points if 8 or fewer
            for i, (d, b) in enumerate(zip(dates, bmis)):
                offset_y = 12 if i % 2 == 0 else -18
                ax.annotate(
                    f"{b:.2f}",
                    xy=(d, b),
                    xytext=(0, offset_y),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8.5,
                    fontweight="bold",
                    color=THEME["text"],
                    bbox=dict(boxstyle="round,pad=0.2", fc=THEME["card_bg"], ec=THEME["line"], lw=0.8, alpha=0.9)
                )
        else:
            # Annotate first, latest, min, and max points for clean readability
            indices_to_label = {0, len(dates) - 1, bmis.index(min_val), bmis.index(max_val)}
            for idx in indices_to_label:
                d = dates[idx]
                b = bmis[idx]
                tag = "Latest: " if idx == len(dates) - 1 else ""
                ax.annotate(
                    f"{tag}{b:.2f}",
                    xy=(d, b),
                    xytext=(0, 12),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8.5,
                    fontweight="bold",
                    color=THEME["text"],
                    bbox=dict(boxstyle="round,pad=0.2", fc=THEME["card_bg"], ec=THEME["line"], lw=0.9)
                )

        # Date formatting for X-axis
        time_span = (dates[-1] - dates[0]).total_seconds()
        if time_span > 86400 * 365:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        elif time_span > 86400 * 3:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d\n%Y"))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d\n%H:%M"))
        figure.autofmt_xdate(rotation=0, ha="center")

    # Grid styling
    ax.grid(True, linestyle=":", alpha=0.3, color=THEME["grid"])

    # Spine styling
    for spine in ax.spines.values():
        spine.set_color(THEME["grid"])

    # Legend with compact modern look
    legend = ax.legend(
        loc="upper left",
        fontsize=8,
        facecolor=THEME["card_bg"],
        edgecolor=THEME["grid"],
        labelcolor=THEME["text"]
    )
    legend.get_frame().set_alpha(0.85)

    figure.tight_layout(pad=1.2)


def create_bmi_figure(records: List[Dict[str, Any]], user_name: str, figsize=(6.5, 4.0), dpi=100) -> Figure:
    """
    Create a standalone Matplotlib Figure for the user's BMI records.

    Returns:
        Configured Figure object ready for display or embedding.
    """
    fig = Figure(figsize=figsize, dpi=dpi)
    render_bmi_chart(fig, records, user_name)
    return fig
