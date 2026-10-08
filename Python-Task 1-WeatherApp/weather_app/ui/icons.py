"""Vector-like procedural weather icon and solar arc renderer using Tkinter Canvas geometry."""

import math
import tkinter as tk
from typing import Optional


class WeatherIconCanvas(tk.Canvas):
    """
    Crisp, resolution-independent vector weather icon rendered directly on a Tkinter Canvas.
    Guarantees razor-sharp rendering on high-DPI displays without external image asset dependencies.
    """

    def __init__(
        self,
        master: tk.Widget,
        condition: str = "Clear",
        is_day: bool = True,
        size: int = 48,
        bg: str = "#161B22",
        **kwargs
    ):
        super().__init__(
            master,
            width=size,
            height=size,
            bg=bg,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.size = size
        self.condition = condition
        self.is_day = is_day
        self.bg_color = bg
        self.render()

    def set_icon(self, condition: str, is_day: bool, bg: Optional[str] = None) -> None:
        """Update and repaint the weather glyph."""
        self.condition = condition
        self.is_day = is_day
        if bg:
            self.bg_color = bg
            self.configure(bg=bg)
        self.render()

    def set_canvas_bg(self, bg: str) -> None:
        """Update background color and redraw."""
        self.bg_color = bg
        self.configure(bg=bg)
        self.render()

    def render(self) -> None:
        """Clear canvas and execute specific geometric drawing routines."""
        self.delete("all")
        s = self.size
        cond = (self.condition or "").strip().lower()

        if "thunder" in cond:
            self._draw_thunderstorm(s)
        elif "snow" in cond or "sleet" in cond:
            self._draw_snow(s)
        elif "rain" in cond:
            self._draw_rain(s)
        elif "drizzle" in cond:
            self._draw_drizzle(s)
        elif any(c in cond for c in ["mist", "fog", "haze", "smoke", "dust", "sand", "ash"]):
            self._draw_atmosphere(s)
        elif "cloud" in cond:
            self._draw_clouds(s)
        else:
            if self.is_day:
                self._draw_sun(s)
            else:
                self._draw_moon(s)

    def _draw_sun(self, s: float) -> None:
        """Draw radiant sun with center circle and eight cardinal/diagonal rays."""
        cx = cy = s / 2.0
        r_core = s * 0.22
        sun_color = "#F59E0B"
        ray_color = "#FBBF24"

        self.create_oval(
            cx - r_core, cy - r_core,
            cx + r_core, cy + r_core,
            fill=sun_color, outline=sun_color
        )

        r_inner = s * 0.30
        r_outer = s * 0.42
        ray_width = max(2, int(s * 0.05))

        for i in range(8):
            angle = i * (math.pi / 4.0)
            x1 = cx + r_inner * math.cos(angle)
            y1 = cy + r_inner * math.sin(angle)
            x2 = cx + r_outer * math.cos(angle)
            y2 = cy + r_outer * math.sin(angle)
            self.create_line(
                x1, y1, x2, y2,
                fill=ray_color,
                width=ray_width,
                capstyle=tk.ROUND
            )

    def _draw_moon(self, s: float) -> None:
        """Draw celestial crescent moon with subtle accent star."""
        cx = s * 0.48
        cy = s * 0.50
        r = s * 0.28
        moon_color = "#C7D2FE"
        shadow_bg = self.bg_color

        self.create_oval(
            cx - r, cy - r,
            cx + r, cy + r,
            fill=moon_color, outline=moon_color
        )

        offset_x = s * 0.16
        offset_y = -s * 0.08
        r_cut = r * 0.95
        self.create_oval(
            (cx + offset_x) - r_cut, (cy + offset_y) - r_cut,
            (cx + offset_x) + r_cut, (cy + offset_y) + r_cut,
            fill=shadow_bg, outline=shadow_bg
        )

        star_x = s * 0.76
        star_y = s * 0.32
        star_r = max(1.5, s * 0.035)
        self.create_oval(
            star_x - star_r, star_y - star_r,
            star_x + star_r, star_y + star_r,
            fill="#E0E7FF", outline="#E0E7FF"
        )

    def _draw_clouds(self, s: float) -> None:
        """Draw layered cloud silhouette."""
        cloud_color = "#94A3B8"
        highlight_color = "#CBD5E1"

        self.create_oval(
            s * 0.22, s * 0.44,
            s * 0.50, s * 0.72,
            fill=cloud_color, outline=cloud_color
        )
        self.create_oval(
            s * 0.38, s * 0.28,
            s * 0.70, s * 0.62,
            fill=highlight_color, outline=highlight_color
        )
        self.create_oval(
            s * 0.54, s * 0.42,
            s * 0.82, s * 0.70,
            fill=cloud_color, outline=cloud_color
        )
        self.create_rectangle(
            s * 0.30, s * 0.54,
            s * 0.74, s * 0.70,
            fill=cloud_color, outline=cloud_color
        )

    def _draw_rain(self, s: float) -> None:
        """Draw cloud with angled rain streaks."""
        self._draw_clouds(s)
        rain_color = "#60A5FA"
        streak_w = max(2, int(s * 0.045))
        streak_len = s * 0.16

        x_coords = [s * 0.32, s * 0.52, s * 0.72]
        y_start = s * 0.74

        for x in x_coords:
            self.create_line(
                x, y_start,
                x - s * 0.06, y_start + streak_len,
                fill=rain_color,
                width=streak_w,
                capstyle=tk.ROUND
            )

    def _draw_drizzle(self, s: float) -> None:
        """Draw cloud with small dotted droplets."""
        self._draw_clouds(s)
        rain_color = "#93C5FD"
        drop_r = max(1.5, s * 0.03)

        coords = [
            (s * 0.35, s * 0.78),
            (s * 0.52, s * 0.84),
            (s * 0.68, s * 0.78)
        ]
        for x, y in coords:
            self.create_oval(
                x - drop_r, y - drop_r,
                x + drop_r, y + drop_r,
                fill=rain_color, outline=rain_color
            )

    def _draw_thunderstorm(self, s: float) -> None:
        """Draw stormy cloud with sharp golden lightning bolt."""
        self._draw_clouds(s)
        bolt_color = "#FBBF24"
        points = [
            s * 0.54, s * 0.68,
            s * 0.44, s * 0.80,
            s * 0.50, s * 0.80,
            s * 0.42, s * 0.94,
            s * 0.58, s * 0.81,
            s * 0.51, s * 0.81
        ]
        self.create_polygon(points, fill=bolt_color, outline=bolt_color)

    def _draw_snow(self, s: float) -> None:
        """Draw cloud with crystalline snowflake."""
        self._draw_clouds(s)
        snow_color = "#E0F2FE"

        cx = s * 0.52
        cy = s * 0.83
        r = s * 0.11
        w = max(1, int(s * 0.035))

        for i in range(3):
            angle = i * (math.pi / 3.0)
            dx = r * math.cos(angle)
            dy = r * math.sin(angle)
            self.create_line(
                cx - dx, cy - dy,
                cx + dx, cy + dy,
                fill=snow_color, width=w, capstyle=tk.ROUND
            )

    def _draw_atmosphere(self, s: float) -> None:
        """Draw layered horizontal atmospheric haze bars (mist/fog)."""
        bar_color = "#94A3B8"
        bar_w = max(2, int(s * 0.05))

        y_positions = [s * 0.36, s * 0.48, s * 0.60, s * 0.72]
        x_spans = [
            (s * 0.22, s * 0.78),
            (s * 0.16, s * 0.84),
            (s * 0.26, s * 0.74),
            (s * 0.20, s * 0.80)
        ]

        for y, (x1, x2) in zip(y_positions, x_spans):
            self.create_line(
                x1, y, x2, y,
                fill=bar_color,
                width=bar_w,
                capstyle=tk.ROUND
            )


class SunArcCanvas(tk.Canvas):
    """
    Subtle celestial sun path arc representation.
    Displays the curved trajectory between sunrise and sunset,
    pinpointing the sun's real-time position during daylight hours.
    """

    def __init__(
        self,
        master: tk.Widget,
        width: int = 240,
        height: int = 95,
        bg: str = "#161B22",
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=bg,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.w = width
        self.h = height
        self.bg_color = bg
        self.sunrise_text = "06:00 AM"
        self.sunset_text = "06:30 PM"
        self.daylight_text = "12h 30m"
        self.progress = 0.5
        self.is_day = True
        self.render()

    def update_sun_cycle(
        self,
        sunrise_str: str,
        sunset_str: str,
        daylight_str: str,
        progress: float,
        is_day: bool,
        bg: Optional[str] = None
    ) -> None:
        """Update solar schedule and re-render."""
        self.sunrise_text = sunrise_str
        self.sunset_text = sunset_str
        self.daylight_text = daylight_str
        self.progress = progress
        self.is_day = is_day
        if bg:
            self.bg_color = bg
            self.configure(bg=bg)
        self.render()

    def set_canvas_bg(self, bg: str) -> None:
        self.bg_color = bg
        self.configure(bg=bg)
        self.render()

    def render(self) -> None:
        """Draw the celestial horizon, arc, and glowing position marker."""
        self.delete("all")
        w, h = self.w, self.h

        # Geometry bounds
        pad_x = 22
        y_horizon = h - 22
        arc_top_y = 16
        arc_cx = w / 2.0
        arc_rx = (w - (pad_x * 2)) / 2.0
        arc_ry = y_horizon - arc_top_y

        # 1. Subtle horizon line
        self.create_line(
            pad_x - 6, y_horizon,
            w - pad_x + 6, y_horizon,
            fill="#2A3447",
            width=1
        )

        # 2. Celestial curve points (semi-ellipse from pad_x to w - pad_x)
        steps = 40
        points = []
        for i in range(steps + 1):
            theta = math.pi * (1.0 - (i / steps))  # pi down to 0
            x = arc_cx + arc_rx * math.cos(theta)
            y = y_horizon - arc_ry * math.sin(theta)
            points.append((x, y))

        # Draw trajectory arc (dashed / dotted)
        for i in range(len(points) - 1):
            self.create_line(
                points[i][0], points[i][1],
                points[i + 1][0], points[i + 1][1],
                fill="#374151" if not self.is_day else "#4B5563",
                dash=(3, 3),
                width=1.5
            )

        # 3. Sunrise and Sunset horizon markers
        # Sunrise (left)
        x_rise = pad_x
        self.create_oval(
            x_rise - 3, y_horizon - 3,
            x_rise + 3, y_horizon + 3,
            fill="#E5A93C", outline="#E5A93C"
        )
        self.create_text(
            x_rise, y_horizon + 12,
            text=f"↑ {self.sunrise_text}",
            fill="#94A3B8",
            font=("Segoe UI", 8, "normal"),
            anchor="center"
        )

        # Sunset (right)
        x_set = w - pad_x
        self.create_oval(
            x_set - 3, y_horizon - 3,
            x_set + 3, y_horizon + 3,
            fill="#E5A93C", outline="#E5A93C"
        )
        self.create_text(
            x_set, y_horizon + 12,
            text=f"↓ {self.sunset_text}",
            fill="#94A3B8",
            font=("Segoe UI", 8, "normal"),
            anchor="center"
        )

        # Center daylight badge
        self.create_text(
            arc_cx, y_horizon + 12,
            text=f"Daylight: {self.daylight_text}",
            fill="#64748B",
            font=("Segoe UI", 8, "bold"),
            anchor="center"
        )

        # 4. Sun or Moon Marker
        if self.is_day and 0.0 <= self.progress <= 1.0:
            # Map progress to position along the semi-ellipse
            theta = math.pi * (1.0 - self.progress)
            sun_x = arc_cx + arc_rx * math.cos(theta)
            sun_y = y_horizon - arc_ry * math.sin(theta)

            # Outer glow
            self.create_oval(
                sun_x - 7, sun_y - 7,
                sun_x + 7, sun_y + 7,
                fill="", outline="#FDE68A", width=1
            )
            # Center bright sun dot
            self.create_oval(
                sun_x - 4, sun_y - 4,
                sun_x + 4, sun_y + 4,
                fill="#F59E0B", outline="#FBBF24"
            )
        else:
            # Night indicator (centered cool moon)
            self.create_text(
                arc_cx, arc_top_y + 12,
                text="☾ Nighttime",
                fill="#818CF8",
                font=("Segoe UI", 9, "bold"),
                anchor="center"
            )
