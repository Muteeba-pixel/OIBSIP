"""
app.py
======
Main GUI Application for the Advanced BMI Calculator & Health Tracker.

Built with Python Tkinter and Matplotlib.
Designed as a modern, portfolio-ready dashboard application.

OASIS Infobyte Python Programming Internship - Task 2
Author: OASIS Intern / Python Developer
"""

import os
import sys
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

# Import Matplotlib Tkinter backend
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Project modules
from bmi_calculator import (
    calculate_bmi,
    classify_bmi,
    validate_inputs,
    BMIValidationError,
    BMIResult,
    CATEGORY_COLORS,
    CATEGORY_UNDERWEIGHT,
    CATEGORY_NORMAL,
    CATEGORY_OVERWEIGHT,
    CATEGORY_OBESE
)
import database
import chart


# ==============================================================================
# UI THEME CONFIGURATION
# ==============================================================================
THEME = {
    "bg_main": "#0f172a",         # Deep slate main window
    "bg_card": "#1e293b",         # Card background
    "bg_input": "#334155",        # Entry background
    "text_primary": "#f8fafc",    # Primary white-ish text
    "text_secondary": "#94a3b8",  # Muted slate text
    "border": "#334155",          # Border line
    "accent_primary": "#0284c7",  # Sky blue primary action
    "accent_hover": "#0369a1",    # Darker blue
    "accent_success": "#16a34a",  # Green
    "accent_danger": "#dc2626",   # Red
    "accent_warning": "#d97706",  # Amber
    "font_family": "Segoe UI" if sys.platform == "win32" else "Helvetica",
}


class BMICalculatorApp(tk.Tk):
    """
    Main application window managing user inputs, BMI computation,
    historical record presentation, and embedded Matplotlib visual trends.
    """

    def __init__(self, db_path: Optional[str] = None):
        super().__init__()

        self.db_path = db_path or database.DEFAULT_DB_PATH

        # Initialize SQLite database
        try:
            database.init_database(self.db_path)
        except database.DatabaseError as err:
            messagebox.showerror("Database Error", f"Failed to initialize database:\n{err}")

        # Window properties
        self.title("BMI Health Tracker & Trend Analyzer — OASIS Infobyte")
        self.geometry("1160x760")
        self.minsize(980, 680)
        self.configure(bg=THEME["bg_main"])

        # State variables
        self.unit_system_var = tk.StringVar(value="metric")
        self.user_name_var = tk.StringVar(value="Default User")
        self.weight_var = tk.StringVar(value="")
        self.height_var = tk.StringVar(value="")
        self.notes_var = tk.StringVar(value="")
        self.current_result: Optional[BMIResult] = None

        # Setup custom modern ttk styling
        self._configure_styles()

        # Build layout components
        self._create_header()
        self._create_main_layout()
        self._create_footer()

        # Initial data loading
        self._reload_user_list()
        self._on_user_changed()

    # --------------------------------------------------------------------------
    # Styling Configuration
    # --------------------------------------------------------------------------
    def _configure_styles(self) -> None:
        """Configure ttk styles for a sleek modern dashboard appearance."""
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        font_name = THEME["font_family"]

        # Base Frame & Label styles
        self.style.configure("Main.TFrame", background=THEME["bg_main"])
        self.style.configure("Card.TFrame", background=THEME["bg_card"], relief="flat")
        self.style.configure(
            "CardTitle.TLabel",
            background=THEME["bg_card"],
            foreground=THEME["text_primary"],
            font=(font_name, 12, "bold")
        )
        self.style.configure(
            "CardSub.TLabel",
            background=THEME["bg_card"],
            foreground=THEME["text_secondary"],
            font=(font_name, 9)
        )
        self.style.configure(
            "CardBody.TLabel",
            background=THEME["bg_card"],
            foreground=THEME["text_primary"],
            font=(font_name, 10)
        )

        # Combobox style
        self.style.configure(
            "TCombobox",
            fieldbackground=THEME["bg_input"],
            background=THEME["bg_card"],
            foreground=THEME["text_primary"],
            darkcolor=THEME["border"],
            lightcolor=THEME["border"],
            arrowcolor=THEME["text_primary"],
            font=(font_name, 10)
        )

        # Radiobutton style
        self.style.configure(
            "TRadiobutton",
            background=THEME["bg_card"],
            foreground=THEME["text_primary"],
            font=(font_name, 10),
            indicatorcolor=THEME["bg_input"],
            indicatormargin=4
        )
        self.style.map(
            "TRadiobutton",
            background=[("active", THEME["bg_card"])],
            foreground=[("active", THEME["text_primary"])]
        )

        # Modern Button Styles
        self.style.configure(
            "Primary.TButton",
            font=(font_name, 10, "bold"),
            background=THEME["accent_primary"],
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            padding=(12, 8)
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", THEME["accent_hover"]), ("pressed", "#075985")]
        )

        self.style.configure(
            "Success.TButton",
            font=(font_name, 10, "bold"),
            background=THEME["accent_success"],
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            padding=(12, 8)
        )
        self.style.map(
            "Success.TButton",
            background=[("active", "#15803d"), ("pressed", "#166534")]
        )

        self.style.configure(
            "Secondary.TButton",
            font=(font_name, 10),
            background=THEME["bg_input"],
            foreground=THEME["text_primary"],
            borderwidth=0,
            focusthickness=0,
            padding=(10, 7)
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", "#475569"), ("pressed", "#1e293b")]
        )

        self.style.configure(
            "Danger.TButton",
            font=(font_name, 9),
            background=THEME["accent_danger"],
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            padding=(8, 5)
        )
        self.style.map(
            "Danger.TButton",
            background=[("active", "#b91c1c")]
        )

        # Modern Notebook (Tabs)
        self.style.configure(
            "TNotebook",
            background=THEME["bg_main"],
            borderwidth=0
        )
        self.style.configure(
            "TNotebook.Tab",
            background=THEME["bg_card"],
            foreground=THEME["text_secondary"],
            font=(font_name, 10, "bold"),
            padding=(14, 8),
            borderwidth=0
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", THEME["bg_input"])],
            foreground=[("selected", THEME["text_primary"])]
        )

        # Treeview (Table) Styling
        self.style.configure(
            "Treeview",
            background=THEME["bg_card"],
            fieldbackground=THEME["bg_card"],
            foreground=THEME["text_primary"],
            font=(font_name, 9),
            rowheight=26,
            borderwidth=0
        )
        self.style.configure(
            "Treeview.Heading",
            background=THEME["bg_input"],
            foreground=THEME["text_primary"],
            font=(font_name, 9, "bold"),
            padding=(6, 6)
        )
        self.style.map(
            "Treeview",
            background=[("selected", THEME["accent_primary"])],
            foreground=[("selected", "#ffffff")]
        )

    # --------------------------------------------------------------------------
    # Header Section
    # --------------------------------------------------------------------------
    def _create_header(self) -> None:
        """Create the top branded navigation header."""
        header_frame = tk.Frame(self, bg=THEME["bg_card"], height=64)
        header_frame.pack(fill=tk.X, side=tk.TOP, padx=0, pady=0)
        header_frame.pack_propagate(False)

        inner = tk.Frame(header_frame, bg=THEME["bg_card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        # Title & Subtitle
        title_box = tk.Frame(inner, bg=THEME["bg_card"])
        title_box.pack(side=tk.LEFT)

        app_title = tk.Label(
            title_box,
            text="⚖️  Advanced BMI Calculator & Health Tracker",
            font=(THEME["font_family"], 15, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_primary"]
        )
        app_title.pack(anchor="w")

        subtitle = tk.Label(
            title_box,
            text="OASIS Infobyte Python Programming Internship (Task 2) • Multi-User Analytics Dashboard",
            font=(THEME["font_family"], 9),
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"]
        )
        subtitle.pack(anchor="w")

        # Current User Badge on Header Right
        self.user_badge = tk.Label(
            inner,
            text="👤 User: Default User",
            font=(THEME["font_family"], 10, "bold"),
            bg=THEME["bg_input"],
            fg=THEME["text_primary"],
            padx=12,
            pady=4,
            relief="flat"
        )
        self.user_badge.pack(side=tk.RIGHT, pady=4)

    # --------------------------------------------------------------------------
    # Main Dashboard Layout
    # --------------------------------------------------------------------------
    def _create_main_layout(self) -> None:
        """Create the two-column responsive master-detail dashboard."""
        content = tk.Frame(self, bg=THEME["bg_main"])
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # Left Column: User Inputs, Calculation Controls, and Visual Result
        left_col = tk.Frame(content, bg=THEME["bg_main"], width=420)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_col.pack_propagate(False)

        # Right Column: Historical Data & Trend Chart Tabs
        right_col = tk.Frame(content, bg=THEME["bg_main"])
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_user_profile_card(left_col)
        self._build_input_card(left_col)
        self._build_result_card(left_col)

        self._build_tabs_section(right_col)

    # --------------------------------------------------------------------------
    # Left Column: User Profile Card
    # --------------------------------------------------------------------------
    def _build_user_profile_card(self, parent: tk.Widget) -> None:
        """Card for selecting or entering multiple named users."""
        card = tk.Frame(parent, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        card.pack(fill=tk.X, pady=(0, 10), ipady=8, ipadx=12)

        header = tk.Label(
            card,
            text="1. User Profile",
            font=(THEME["font_family"], 11, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_primary"]
        )
        header.pack(anchor="w", padx=10, pady=(6, 6))

        row = tk.Frame(card, bg=THEME["bg_card"])
        row.pack(fill=tk.X, padx=10)

        lbl = tk.Label(
            row,
            text="Select or Enter User:",
            font=(THEME["font_family"], 9),
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"]
        )
        lbl.pack(anchor="w", pady=(0, 3))

        user_input_frame = tk.Frame(row, bg=THEME["bg_card"])
        user_input_frame.pack(fill=tk.X)

        self.user_combo = ttk.Combobox(
            user_input_frame,
            textvariable=self.user_name_var,
            font=(THEME["font_family"], 10)
        )
        self.user_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_combo.bind("<<ComboboxSelected>>", lambda e: self._on_user_changed())
        self.user_combo.bind("<Return>", lambda e: self._on_user_changed())

        btn_switch = ttk.Button(
            user_input_frame,
            text="Load",
            style="Secondary.TButton",
            command=self._on_user_changed
        )
        btn_switch.pack(side=tk.LEFT, padx=(6, 0))

    # --------------------------------------------------------------------------
    # Left Column: Measurements Input Card
    # --------------------------------------------------------------------------
    def _build_input_card(self, parent: tk.Widget) -> None:
        """Card for entering height, weight, unit toggles, and calculation actions."""
        card = tk.Frame(parent, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        card.pack(fill=tk.X, pady=(0, 10), ipady=8, ipadx=12)

        header = tk.Label(
            card,
            text="2. Body Measurements",
            font=(THEME["font_family"], 11, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_primary"]
        )
        header.pack(anchor="w", padx=10, pady=(6, 6))

        # Unit Selector Toggle
        unit_frame = tk.Frame(card, bg=THEME["bg_card"])
        unit_frame.pack(fill=tk.X, padx=10, pady=(0, 8))

        unit_lbl = tk.Label(
            unit_frame,
            text="Measurement Units:",
            font=(THEME["font_family"], 9),
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"]
        )
        unit_lbl.pack(side=tk.LEFT)

        r_metric = ttk.Radiobutton(
            unit_frame,
            text="Metric (kg, cm)",
            value="metric",
            variable=self.unit_system_var,
            command=self._on_unit_system_changed
        )
        r_metric.pack(side=tk.LEFT, padx=(12, 6))

        r_imperial = ttk.Radiobutton(
            unit_frame,
            text="Imperial (lbs, in)",
            value="imperial",
            variable=self.unit_system_var,
            command=self._on_unit_system_changed
        )
        r_imperial.pack(side=tk.LEFT, padx=6)

        # Inputs Grid
        grid = tk.Frame(card, bg=THEME["bg_card"])
        grid.pack(fill=tk.X, padx=10, pady=4)
        grid.columnconfigure(1, weight=1)

        # Weight Row
        self.lbl_weight = tk.Label(
            grid,
            text="Weight (kg):",
            font=(THEME["font_family"], 10),
            bg=THEME["bg_card"],
            fg=THEME["text_primary"]
        )
        self.lbl_weight.grid(row=0, column=0, sticky="w", pady=6)

        self.entry_weight = tk.Entry(
            grid,
            textvariable=self.weight_var,
            font=(THEME["font_family"], 10),
            bg=THEME["bg_input"],
            fg=THEME["text_primary"],
            insertbackground=THEME["text_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["accent_primary"]
        )
        self.entry_weight.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=6, ipady=4)
        self.entry_weight.bind("<Return>", lambda e: self.calculate_and_display())

        # Height Row
        self.lbl_height = tk.Label(
            grid,
            text="Height (cm):",
            font=(THEME["font_family"], 10),
            bg=THEME["bg_card"],
            fg=THEME["text_primary"]
        )
        self.lbl_height.grid(row=1, column=0, sticky="w", pady=6)

        self.entry_height = tk.Entry(
            grid,
            textvariable=self.height_var,
            font=(THEME["font_family"], 10),
            bg=THEME["bg_input"],
            fg=THEME["text_primary"],
            insertbackground=THEME["text_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["accent_primary"]
        )
        self.entry_height.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=6, ipady=4)
        self.entry_height.bind("<Return>", lambda e: self.calculate_and_display())

        # Optional Notes Row
        lbl_notes = tk.Label(
            grid,
            text="Notes (opt):",
            font=(THEME["font_family"], 10),
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"]
        )
        lbl_notes.grid(row=2, column=0, sticky="w", pady=6)

        entry_notes = tk.Entry(
            grid,
            textvariable=self.notes_var,
            font=(THEME["font_family"], 10),
            bg=THEME["bg_input"],
            fg=THEME["text_primary"],
            insertbackground=THEME["text_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        entry_notes.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=6, ipady=4)

        # Action Buttons
        btn_bar = tk.Frame(card, bg=THEME["bg_card"])
        btn_bar.pack(fill=tk.X, padx=10, pady=(12, 4))

        btn_calc = ttk.Button(
            btn_bar,
            text="⚡ Calculate BMI",
            style="Primary.TButton",
            command=self.calculate_and_display
        )
        btn_calc.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_save = ttk.Button(
            btn_bar,
            text="💾 Save Record",
            style="Success.TButton",
            command=self.save_current_record
        )
        self.btn_save.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        btn_reset = ttk.Button(
            btn_bar,
            text="🔄 Reset",
            style="Secondary.TButton",
            command=self.reset_inputs
        )
        btn_reset.pack(side=tk.LEFT, padx=(4, 0))

    # --------------------------------------------------------------------------
    # Left Column: Calculated Result Card
    # --------------------------------------------------------------------------
    def _build_result_card(self, parent: tk.Widget) -> None:
        """Card displaying real-time BMI score, category badge, and health metrics."""
        self.res_card = tk.Frame(parent, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        self.res_card.pack(fill=tk.BOTH, expand=True, ipady=6, ipadx=12)

        header = tk.Label(
            self.res_card,
            text="3. BMI Assessment Result",
            font=(THEME["font_family"], 11, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_primary"]
        )
        header.pack(anchor="w", padx=10, pady=(6, 4))

        # Big BMI Number
        self.lbl_bmi_value = tk.Label(
            self.res_card,
            text="--.--",
            font=(THEME["font_family"], 34, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"]
        )
        self.lbl_bmi_value.pack(pady=(4, 2))

        # Category Badge (Pill)
        self.badge_category = tk.Label(
            self.res_card,
            text="Awaiting Calculation",
            font=(THEME["font_family"], 10, "bold"),
            bg=THEME["bg_input"],
            fg=THEME["text_secondary"],
            padx=14,
            pady=4
        )
        self.badge_category.pack(pady=4)

        # Visual BMI Gauge Scale
        self._build_gauge_visual(self.res_card)

        # Healthy Weight Range text
        self.lbl_healthy_range = tk.Label(
            self.res_card,
            text="Healthy Weight Range: --",
            font=(THEME["font_family"], 9, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_primary"]
        )
        self.lbl_healthy_range.pack(pady=(6, 2))

        # Dynamic Recommendation Box
        self.lbl_recommendation = tk.Label(
            self.res_card,
            text="Enter weight and height above, then click 'Calculate BMI'.",
            font=(THEME["font_family"], 9),
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            wraplength=340,
            justify=tk.CENTER
        )
        self.lbl_recommendation.pack(pady=(2, 6), padx=10)

    def _build_gauge_visual(self, parent: tk.Widget) -> None:
        """Draw an informative 4-segment WHO category bar inside the result card."""
        gauge_container = tk.Frame(parent, bg=THEME["bg_card"])
        gauge_container.pack(fill=tk.X, padx=16, pady=6)

        # Colored bands representing categories
        bar_frame = tk.Frame(gauge_container, height=12, bg=THEME["bg_input"])
        bar_frame.pack(fill=tk.X)
        bar_frame.pack_propagate(False)

        # 4 segments
        b1 = tk.Frame(bar_frame, bg=CATEGORY_COLORS[CATEGORY_UNDERWEIGHT])
        b1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        b2 = tk.Frame(bar_frame, bg=CATEGORY_COLORS[CATEGORY_NORMAL])
        b2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        b3 = tk.Frame(bar_frame, bg=CATEGORY_COLORS[CATEGORY_OVERWEIGHT])
        b3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        b4 = tk.Frame(bar_frame, bg=CATEGORY_COLORS[CATEGORY_OBESE])
        b4.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Labels beneath the gauge
        lbl_frame = tk.Frame(gauge_container, bg=THEME["bg_card"])
        lbl_frame.pack(fill=tk.X, pady=(2, 0))

        for text, col in [
            ("< 18.5\nUnder", CATEGORY_COLORS[CATEGORY_UNDERWEIGHT]),
            ("18.5 - 24.9\nNormal", CATEGORY_COLORS[CATEGORY_NORMAL]),
            ("25 - 29.9\nOver", CATEGORY_COLORS[CATEGORY_OVERWEIGHT]),
            ("≥ 30\nObese", CATEGORY_COLORS[CATEGORY_OBESE])
        ]:
            lbl = tk.Label(
                lbl_frame,
                text=text,
                font=(THEME["font_family"], 7),
                bg=THEME["bg_card"],
                fg=col,
                justify=tk.CENTER
            )
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # --------------------------------------------------------------------------
    # Right Column: Tabs Section (Chart, Table, Guide)
    # --------------------------------------------------------------------------
    def _build_tabs_section(self, parent: tk.Widget) -> None:
        """Create the tabbed notebook for Trend Chart, History Records, and Guide."""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: BMI Trend Chart
        self.tab_chart = tk.Frame(self.notebook, bg=THEME["bg_card"])
        self.notebook.add(self.tab_chart, text="  📈  BMI Trend Chart  ")
        self._build_chart_tab(self.tab_chart)

        # Tab 2: History Records Table
        self.tab_history = tk.Frame(self.notebook, bg=THEME["bg_card"])
        self.notebook.add(self.tab_history, text="  📋  Historical Records  ")
        self._build_history_tab(self.tab_history)

        # Tab 3: BMI Reference Guide
        self.tab_guide = tk.Frame(self.notebook, bg=THEME["bg_card"])
        self.notebook.add(self.tab_guide, text="  ℹ️  BMI Reference Guide  ")
        self._build_guide_tab(self.tab_guide)

    # --------------------------------------------------------------------------
    # Tab 1: Matplotlib Chart Tab
    # --------------------------------------------------------------------------
    def _build_chart_tab(self, parent: tk.Widget) -> None:
        """Embed an interactive Matplotlib chart canvas inside Tkinter."""
        top_bar = tk.Frame(parent, bg=THEME["bg_card"])
        top_bar.pack(fill=tk.X, padx=12, pady=(10, 4))

        self.lbl_chart_summary = tk.Label(
            top_bar,
            text="Tracking history trajectory for selected user",
            font=(THEME["font_family"], 9),
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"]
        )
        self.lbl_chart_summary.pack(side=tk.LEFT)

        btn_refresh_chart = ttk.Button(
            top_bar,
            text="🔄 Refresh Chart",
            style="Secondary.TButton",
            command=self._refresh_chart
        )
        btn_refresh_chart.pack(side=tk.RIGHT)

        # Canvas for Matplotlib figure
        self.fig = Figure(figsize=(6.2, 4.4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 12))
        self.canvas_widget.configure(bg=THEME["bg_card"])

    # --------------------------------------------------------------------------
    # Tab 2: Historical Records Table Tab
    # --------------------------------------------------------------------------
    def _build_history_tab(self, parent: tk.Widget) -> None:
        """Create the Treeview table displaying user records with action buttons."""
        action_bar = tk.Frame(parent, bg=THEME["bg_card"])
        action_bar.pack(fill=tk.X, padx=12, pady=(10, 6))

        self.lbl_table_count = tk.Label(
            action_bar,
            text="0 records found",
            font=(THEME["font_family"], 9, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"]
        )
        self.lbl_table_count.pack(side=tk.LEFT)

        btn_export = ttk.Button(
            action_bar,
            text="📥 Export to CSV",
            style="Secondary.TButton",
            command=self.export_records_to_csv
        )
        btn_export.pack(side=tk.RIGHT, padx=(6, 0))

        btn_delete_selected = ttk.Button(
            action_bar,
            text="🗑️ Delete Selected",
            style="Danger.TButton",
            command=self.delete_selected_record
        )
        btn_delete_selected.pack(side=tk.RIGHT, padx=6)

        btn_clear_all = ttk.Button(
            action_bar,
            text="⚠️ Clear All History",
            style="Danger.TButton",
            command=self.clear_all_user_records
        )
        btn_clear_all.pack(side=tk.RIGHT)

        # Treeview Table
        table_container = tk.Frame(parent, bg=THEME["bg_card"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 12))

        columns = ("id", "date", "weight", "height", "bmi", "category", "notes")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date & Time")
        self.tree.heading("weight", text="Weight (kg)")
        self.tree.heading("height", text="Height (m)")
        self.tree.heading("bmi", text="BMI")
        self.tree.heading("category", text="Category")
        self.tree.heading("notes", text="Notes")

        self.tree.column("id", width=45, anchor=tk.CENTER)
        self.tree.column("date", width=145, anchor=tk.CENTER)
        self.tree.column("weight", width=85, anchor=tk.CENTER)
        self.tree.column("height", width=85, anchor=tk.CENTER)
        self.tree.column("bmi", width=75, anchor=tk.CENTER)
        self.tree.column("category", width=110, anchor=tk.CENTER)
        self.tree.column("notes", width=160, anchor=tk.W)

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        table_container.rowconfigure(0, weight=1)
        table_container.columnconfigure(0, weight=1)

    # --------------------------------------------------------------------------
    # Tab 3: BMI Reference Guide Tab
    # --------------------------------------------------------------------------
    def _build_guide_tab(self, parent: tk.Widget) -> None:
        """Informational tab showing WHO BMI standards, formulas, and guidance."""
        container = tk.Frame(parent, bg=THEME["bg_card"])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        title = tk.Label(
            container,
            text="World Health Organization (WHO) BMI Classification",
            font=(THEME["font_family"], 12, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_primary"]
        )
        title.pack(anchor="w", pady=(0, 10))

        # Categories explanation table
        guide_items = [
            ("Underweight", "< 18.5", "Higher risk of nutritional deficiency and osteoporosis.", CATEGORY_COLORS[CATEGORY_UNDERWEIGHT]),
            ("Normal Weight", "18.5 – 24.9", "Lowest statistical risk for cardiovascular diseases.", CATEGORY_COLORS[CATEGORY_NORMAL]),
            ("Overweight", "25.0 – 29.9", "Increased risk of hypertension and type 2 diabetes.", CATEGORY_COLORS[CATEGORY_OVERWEIGHT]),
            ("Obese (Class I+)", "≥ 30.0", "High clinical risk for chronic cardiometabolic conditions.", CATEGORY_COLORS[CATEGORY_OBESE]),
        ]

        for cat, range_str, desc, col in guide_items:
            row = tk.Frame(container, bg=THEME["bg_input"], padx=12, pady=8)
            row.pack(fill=tk.X, pady=4)

            badge = tk.Label(
                row,
                text=f" {cat} ({range_str}) ",
                font=(THEME["font_family"], 9, "bold"),
                bg=col,
                fg="#ffffff",
                padx=6,
                pady=2
            )
            badge.pack(side=tk.LEFT)

            desc_lbl = tk.Label(
                row,
                text=desc,
                font=(THEME["font_family"], 9),
                bg=THEME["bg_input"],
                fg=THEME["text_primary"],
                padx=10
            )
            desc_lbl.pack(side=tk.LEFT)

        # Mathematical Formula Info
        formula_box = tk.LabelFrame(
            container,
            text=" Mathematical Formulas Used ",
            font=(THEME["font_family"], 10, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_primary"],
            padx=12,
            pady=10
        )
        formula_box.pack(fill=tk.X, pady=(16, 0))

        formula_text = (
            "• Metric System:      BMI = Weight (kg) / [Height (m)]²\n"
            "• Imperial System:    BMI = [Weight (lbs) / Height (in)²] × 703  "
            "(Converted internally to standard SI units)\n"
            "• Healthy Weight:    Min = 18.5 × [Height (m)]², Max = 24.9 × [Height (m)]²"
        )
        lbl_f = tk.Label(
            formula_box,
            text=formula_text,
            font=("Consolas" if sys.platform == "win32" else "Courier", 9),
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            justify=tk.LEFT
        )
        lbl_f.pack(anchor="w")

    # --------------------------------------------------------------------------
    # Footer Section: Disclaimer
    # --------------------------------------------------------------------------
    def _create_footer(self) -> None:
        """Render the medical disclaimer footer banner."""
        footer = tk.Frame(self, bg="#020617", height=32)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        disclaimer_text = (
            "⚠️ Disclaimer: This BMI Health Tracker is for educational and informational purposes only. "
            "BMI does not directly measure body fat or muscle mass. Always consult a qualified medical professional for health evaluations."
        )
        lbl = tk.Label(
            footer,
            text=disclaimer_text,
            font=(THEME["font_family"], 8),
            bg="#020617",
            fg=THEME["text_secondary"]
        )
        lbl.pack(expand=True, pady=6)

    # --------------------------------------------------------------------------
    # Event Handlers & Core Interactions
    # --------------------------------------------------------------------------
    def _on_unit_system_changed(self) -> None:
        """Update input field labels when switching between Metric and Imperial."""
        system = self.unit_system_var.get()
        if system == "metric":
            self.lbl_weight.config(text="Weight (kg):")
            self.lbl_height.config(text="Height (cm):")
        else:
            self.lbl_weight.config(text="Weight (lbs):")
            self.lbl_height.config(text="Height (in):")

    def _reload_user_list(self) -> None:
        """Fetch distinct user names from the database and populate Combobox."""
        try:
            users = database.get_users(self.db_path)
            if not users:
                users = ["Default User"]
            self.user_combo["values"] = users
        except database.DatabaseError as err:
            messagebox.showerror("Database Error", f"Unable to fetch user list:\n{err}")

    def _on_user_changed(self) -> None:
        """Handle switching to another user: update badge, table, and trend chart."""
        current_name = self.user_name_var.get().strip() or "Default User"
        self.user_badge.config(text=f"👤 User: {current_name}")
        self._refresh_history_table()
        self._refresh_chart()

    def calculate_and_display(self) -> Optional[BMIResult]:
        """Validate inputs, calculate BMI, and update visual result components."""
        weight_raw = self.weight_var.get()
        height_raw = self.height_var.get()
        unit_system = self.unit_system_var.get()
        user_name = self.user_name_var.get().strip() or "Default User"

        try:
            result = calculate_bmi(
                weight_raw=weight_raw,
                height_raw=height_raw,
                unit_system=unit_system,
                user_name=user_name
            )
        except BMIValidationError as val_err:
            messagebox.showwarning("Validation Notice", str(val_err))
            return None
        except Exception as exc:
            messagebox.showerror("Calculation Error", f"Unexpected error during calculation:\n{exc}")
            return None

        # Store calculation result in memory
        self.current_result = result

        # Update Result Card Visuals
        self.lbl_bmi_value.config(text=result.bmi_formatted, fg=result.color_hex)
        self.badge_category.config(
            text=f"● {result.category.upper()} (BMI: {result.bmi_formatted})",
            bg=result.color_hex,
            fg="#ffffff"
        )
        self.lbl_healthy_range.config(
            text=f"Target Healthy Weight: {result.healthy_range_formatted}"
        )
        self.lbl_recommendation.config(text=result.recommendation)

        return result

    def save_current_record(self) -> None:
        """Save the currently displayed calculation into the SQLite database."""
        # If user hasn't calculated yet, calculate first
        if self.current_result is None:
            self.current_result = self.calculate_and_display()
            if self.current_result is None:
                return

        user_name = self.user_name_var.get().strip() or "Default User"
        notes = self.notes_var.get().strip()

        try:
            record_id = database.add_record(
                user_name=user_name,
                weight=self.current_result.weight_kg,
                height=self.current_result.height_m,
                bmi=self.current_result.bmi,
                category=self.current_result.category,
                notes=notes,
                db_path=self.db_path
            )
            # Update user list in dropdown if this was a new user
            self._reload_user_list()
            self._refresh_history_table()
            self._refresh_chart()

            messagebox.showinfo(
                "Record Saved",
                f"Successfully saved BMI record #{record_id} for '{user_name}'!\n"
                f"BMI: {self.current_result.bmi_formatted} ({self.current_result.category})"
            )
        except database.DatabaseError as db_err:
            messagebox.showerror("Database Save Error", f"Could not save record:\n{db_err}")

    def reset_inputs(self) -> None:
        """Clear all measurement inputs and reset result presentation to initial state."""
        self.weight_var.set("")
        self.height_var.set("")
        self.notes_var.set("")
        self.current_result = None

        self.lbl_bmi_value.config(text="--.--", fg=THEME["text_secondary"])
        self.badge_category.config(
            text="Awaiting Calculation",
            bg=THEME["bg_input"],
            fg=THEME["text_secondary"]
        )
        self.lbl_healthy_range.config(text="Healthy Weight Range: --")
        self.lbl_recommendation.config(
            text="Enter weight and height above, then click 'Calculate BMI'."
        )
        self.entry_weight.focus_set()

    def _refresh_history_table(self) -> None:
        """Reload historical records for the active user into the Treeview."""
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        user_name = self.user_name_var.get().strip() or "Default User"

        try:
            records = database.get_user_records(user_name, order="DESC", db_path=self.db_path)
            self.lbl_table_count.config(
                text=f"{len(records)} record{'s' if len(records) != 1 else ''} for '{user_name}'"
            )

            for rec in records:
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        rec["id"],
                        rec["created_at"],
                        f"{rec['weight']:.1f}",
                        f"{rec['height']:.2f}",
                        f"{rec['bmi']:.2f}",
                        rec["category"],
                        rec["notes"] or ""
                    )
                )
        except database.DatabaseError as err:
            messagebox.showerror("Database Read Error", f"Failed to load records:\n{err}")

    def _refresh_chart(self) -> None:
        """Fetch records chronologically and redraw the Matplotlib trend chart."""
        user_name = self.user_name_var.get().strip() or "Default User"
        try:
            records = database.get_user_records(user_name, order="ASC", db_path=self.db_path)
            chart.render_bmi_chart(self.fig, records, user_name)
            self.canvas.draw_idle()
            self.lbl_chart_summary.config(
                text=f"Showing trajectory across {len(records)} recorded entries for '{user_name}'"
            )
        except database.DatabaseError as err:
            messagebox.showerror("Database Error", f"Unable to fetch records for chart:\n{err}")
        except Exception as exc:
            messagebox.showerror("Chart Rendering Error", f"Error updating chart:\n{exc}")

    def delete_selected_record(self) -> None:
        """Delete the currently selected row in the history table."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a record from the table to delete.")
            return

        values = self.tree.item(selected_item[0], "values")
        record_id = int(values[0])
        created_at = values[1]

        confirm = messagebox.askyesno(
            "Confirm Record Deletion",
            f"Are you sure you want to permanently delete record #{record_id} recorded on {created_at}?"
        )
        if not confirm:
            return

        try:
            database.delete_record(record_id, db_path=self.db_path)
            self._refresh_history_table()
            self._refresh_chart()
            messagebox.showinfo("Deleted", f"Record #{record_id} has been removed.")
        except database.DatabaseError as err:
            messagebox.showerror("Database Error", f"Failed to delete record:\n{err}")

    def clear_all_user_records(self) -> None:
        """Clear all records for the active user after explicit confirmation."""
        user_name = self.user_name_var.get().strip() or "Default User"
        confirm = messagebox.askyesno(
            "Confirm Clear All History",
            f"⚠️ DANGER: This will permanently delete ALL historical records for '{user_name}'.\n\nAre you sure you wish to continue?"
        )
        if not confirm:
            return

        try:
            deleted_count = database.clear_user_history(user_name, db_path=self.db_path)
            self._reload_user_list()
            self._refresh_history_table()
            self._refresh_chart()
            messagebox.showinfo("History Cleared", f"Cleared {deleted_count} record(s) for '{user_name}'.")
        except database.DatabaseError as err:
            messagebox.showerror("Database Error", f"Failed to clear history:\n{err}")

    def export_records_to_csv(self) -> None:
        """Export current user records to a user-selected CSV file."""
        user_name = self.user_name_var.get().strip() or "Default User"
        try:
            records = database.get_user_records(user_name, order="ASC", db_path=self.db_path)
            if not records:
                messagebox.showinfo("Export CSV", f"No records to export for '{user_name}'.")
                return

            default_filename = f"bmi_records_{user_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                initialfile=default_filename,
                title="Export BMI History to CSV"
            )
            if not filepath:
                return

            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["id", "user_name", "weight_kg", "height_m", "bmi", "category", "created_at", "notes"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for r in records:
                    writer.writerow({
                        "id": r["id"],
                        "user_name": r["user_name"],
                        "weight_kg": r["weight"],
                        "height_m": r["height"],
                        "bmi": r["bmi"],
                        "category": r["category"],
                        "created_at": r["created_at"],
                        "notes": r["notes"] or ""
                    })

            messagebox.showinfo("Export Successful", f"Exported {len(records)} records to:\n{filepath}")
        except (database.DatabaseError, OSError) as err:
            messagebox.showerror("Export Failed", f"Failed to export CSV:\n{err}")


# ==============================================================================
# Application Entry Point
# ==============================================================================
def main():
    """Main function to launch the application."""
    app = BMICalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
