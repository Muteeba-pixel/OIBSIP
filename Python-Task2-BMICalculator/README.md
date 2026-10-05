# ⚖️ Advanced BMI Calculator & Health Tracker (GUI)

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter GUI](https://img.shields.io/badge/GUI-Tkinter-blue?style=for-the-badge&logo=python)](https://docs.python.org/3/library/tkinter.html)
[![SQLite3](https://img.shields.io/badge/Database-SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Matplotlib](https://img.shields.io/badge/Visualization-Matplotlib-11557C?style=for-the-badge&logo=plotly&logoColor=white)](https://matplotlib.org/)
[![OASIS Infobyte](https://img.shields.io/badge/Internship-OASIS%20Infobyte-FF6F00?style=for-the-badge)](https://oasisinfobyte.com/)

> **OASIS Infobyte Internship Project — Python Programming Internship (Task 2)**  
> Repository Path: `OIBSIP/Python-Task2-BMICalculator/`

---

## 📌 Project Overview

The **Advanced BMI Calculator & Health Tracker** is a portfolio-ready desktop application built with **Python**, **Tkinter**, **SQLite3**, and **Matplotlib**. Designed as a modern dark-themed wellness dashboard, the application calculates Body Mass Index (BMI), provides real-time World Health Organization (WHO) category classification with visual feedback, supports multiple user profiles, persistently logs historical records in an SQLite database, and generates interactive BMI trajectory trend charts over time.

---

## 🌟 Key Features

- **⚡ Instant BMI Calculation**:
  - Computes Body Mass Index using the standard formula:  
    $$\text{BMI} = \frac{\text{Weight (kg)}}{\left[\text{Height (m)}\right]^2}$$
  - Results rounded cleanly to **2 decimal places**.
  - Dual unit support: **Metric (kg, cm)** and **Imperial (lbs, in)** with automatic conversion.

- **🎨 Color-Coded Health Classification (WHO Standard)**:
  - 🔵 **Underweight**: BMI < 18.5
  - 🟢 **Normal Weight**: BMI 18.5 – 24.9
  - 🟠 **Overweight**: BMI 25.0 – 29.9
  - 🔴 **Obese**: BMI ≥ 30.0
  - Includes a visual 4-color category gauge and target healthy weight range calculation.

- **👥 Multi-User Management**:
  - Distinct profiles for multiple family members or clients.
  - Dropdown selection with typeahead to switch users or create new accounts seamlessly.
  - Profile-isolated historical records and trends.

- **💾 Persistent SQLite Database**:
  - Automatic database schema setup with indexed queries.
  - Stores user name, weight, height, BMI, category, exact timestamp, and custom notes.
  - Context-managed transactions with WAL mode and connection safety.

- **📈 Embedded Matplotlib Trend Visualization**:
  - Interactive line chart embedded directly within Tkinter.
  - Plots historical BMI readings over time with dates on the X-axis.
  - Shaded horizontal WHO reference bands to visually gauge progress toward normal weight.

- **📋 Historical Records Management**:
  - Sortable `ttk.Treeview` table displaying all entries.
  - Individual record deletion and user history purge with confirmation dialogs.
  - **Export to CSV** functionality for external reporting.

- **🛡️ Robust Input Validation & Error Handling**:
  - Guards against empty fields, non-numeric characters, zero/negative inputs, and biologically implausible extremes.
  - Friendly GUI message boxes prevent application crashes and guide the user.

---

## 📋 OASIS Requirements Covered

| # | OASIS Infobyte Requirement | Status | Implementation Details |
|---|-----------------------------|:------:|------------------------|
| 1 | Professional GUI application with Tkinter | ✅ Covered | Dark slate dashboard with modern ttk styling and card layout |
| 2 | Input fields for user name, weight, and height | ✅ Covered | Dedicated inputs with metric & imperial unit support |
| 3 | Formula: `BMI = weight / (height ** 2)` | ✅ Covered | Implemented in `bmi_calculator.py` with precision conversion |
| 4 | Categorization (Underweight, Normal, Overweight, Obese) | ✅ Covered | Strict adherence to WHO thresholds |
| 5 | Round BMI to 2 decimal places | ✅ Covered | Formatted as `f"{bmi:.2f}"` |
| 6 | Display BMI category clearly | ✅ Covered | Prominent badge and summary text |
| 7 | Color-coded visual feedback | ✅ Covered | Hex-coded badge, score text, and 4-tier visual gauge |
| 8 | Support multiple named users | ✅ Covered | User profile selector with isolated records |
| 9 | Save records in SQLite database | ✅ Covered | `data/bmi_records.db` with WAL mode and error handling |
| 10 | Display historical records for selected user | ✅ Covered | Interactive `ttk.Treeview` table with scrollbars |
| 11 | BMI trend line chart using Matplotlib | ✅ Covered | Embedded `FigureCanvasTkAgg` chart with reference bands |
| 12 | Graceful database error handling | ✅ Covered | Custom `DatabaseError` with safe context managers |
| 13 | Comprehensive input validation | ✅ Covered | Validates empty, non-numeric, zero, negative, and out-of-range inputs |
| 14 | Friendly error messages in GUI | ✅ Covered | Non-blocking `messagebox` alerts, no unhandled exceptions |
| 15 | Clean, modern professional layout | ✅ Covered | Card-based master-detail layout with Segoe UI typography |
| 16 | Easy for a beginner to understand | ✅ Covered | Clean modular architecture, clear docstrings, and comments |

---

## 🛠️ Technologies Used

- **Programming Language**: Python 3.8+ (Tested on Python 3.14)
- **GUI Framework**: Tkinter & `ttk` (Standard Library)
- **Database**: SQLite3 (Standard Library)
- **Data Visualization**: Matplotlib (`FigureCanvasTkAgg`)
- **Testing Framework**: `unittest` (Standard Library)
- **Exporting**: Python `csv` module (Standard Library)

---

## 📂 Project Structure

```text
BMI-Calculator/
│
├── app.py                  # Main Tkinter GUI application & event controller
├── bmi_calculator.py       # Core calculation, WHO classification & validation logic
├── database.py             # SQLite persistence layer with multi-user CRUD operations
├── chart.py                # Matplotlib visualization with WHO reference bands
├── test_bmi.py             # Automated unit tests covering all 13 core scenarios
├── test_app_gui.py         # End-to-end integration tests for GUI flows
├── requirements.txt        # Third-party dependencies (matplotlib)
├── README.md               # Professional project documentation
├── .gitignore              # Git ignore rules for Python bytecode and databases
└── data/
    └── .gitkeep            # Placeholder keeping data directory in git
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or newer installed on your machine.
- Verify installation by opening a terminal / command prompt:
  ```bash
  python --version
  pip --version
  ```

### Step 1: Clone or Navigate to the Project
```bash
cd "BMI-Calculator"
```

### Step 2: (Optional) Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 How to Run the Application

Execute the entry point script:

```bash
python app.py
```

### Step-by-Step Usage Guide:
1. **Select or Enter User**: Choose an existing user from the dropdown or type a new name (e.g., `Alex`).
2. **Choose Units**: Select **Metric (kg, cm)** or **Imperial (lbs, in)**.
3. **Enter Measurements**:
   - For Metric: Enter weight in kg (e.g., `70`) and height in cm (e.g., `175`) or meters (e.g., `1.75`).
   - For Imperial: Enter weight in lbs (e.g., `160`) and height in inches (e.g., `70`).
4. **Click "⚡ Calculate BMI"**: The result card instantly updates with your BMI value, color-coded badge, visual gauge, and target healthy weight range.
5. **Click "💾 Save Record"**: The record is saved to the SQLite database, and the **BMI Trend Chart** and **Historical Records** table refresh automatically.
6. **Analyze Trends**:
   - Switch to the **📈 BMI Trend Chart** tab to see your BMI trajectory relative to WHO healthy thresholds.
   - Switch to the **📋 Historical Records** tab to view raw entries, delete individual records, or export your history to a `.csv` file.

---

## 🗄️ Database Information

- **Engine**: SQLite3
- **Database File**: `data/bmi_records.db` (created automatically upon first launch)
- **Table Name**: `bmi_records`

### Database Schema:
```sql
CREATE TABLE IF NOT EXISTS bmi_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL COLLATE NOCASE,
    weight REAL NOT NULL,
    height REAL NOT NULL,
    bmi REAL NOT NULL,
    category TEXT NOT NULL,
    created_at TEXT NOT NULL,
    notes TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_user_created 
ON bmi_records (user_name, created_at);
```

---

## 🖼️ Screenshots Section

> *To add screenshots for your OASIS submission or GitHub portfolio:*
> 1. Run `python app.py` and take screenshots of the Main Dashboard, Trend Chart, and History Table.
> 2. Save them into an `assets/` directory (e.g., `assets/dashboard.png`).
> 3. Reference them below.

| Main Dashboard & Calculation | BMI Trend Chart Analytics |
|:---:|:---:|
| *(Add your screenshot here)* | *(Add your screenshot here)* |

| Historical Records & CSV Export | WHO Reference Guide |
|:---:|:---:|
| *(Add your screenshot here)* | *(Add your screenshot here)* |

---

## 🧪 Testing & Verification

The project includes a comprehensive automated test suite with **16 tests** covering calculation precision, edge cases, input validation, multi-user isolation, Matplotlib chart rendering, cross-session database persistence, and GUI flows.

### Running the Test Suite:
```bash
python -m unittest discover -v -p "test_*.py"
```

### Test Results Summary:
```text
test_gui_calculation_and_save_flow (test_app_gui.TestAppGUI) ... ok
test_gui_imperial_units_flow (test_app_gui.TestAppGUI) ... ok
test_01_normal_bmi (test_bmi.TestBMICalculator) ... ok
test_02_underweight_bmi (test_bmi.TestBMICalculator) ... ok
test_03_overweight_bmi (test_bmi.TestBMICalculator) ... ok
test_04_obese_bmi (test_bmi.TestBMICalculator) ... ok
test_05_empty_inputs (test_bmi.TestBMICalculator) ... ok
test_06_non_numeric_inputs (test_bmi.TestBMICalculator) ... ok
test_07_zero_values (test_bmi.TestBMICalculator) ... ok
test_08_negative_values (test_bmi.TestBMICalculator) ... ok
test_09_saving_record (test_bmi.TestBMICalculator) ... ok
test_10_loading_history (test_bmi.TestBMICalculator) ... ok
test_11_multiple_users (test_bmi.TestBMICalculator) ... ok
test_12_bmi_trend_chart (test_bmi.TestBMICalculator) ... ok
test_13_database_error_handling (test_bmi.TestBMICalculator) ... ok
test_14_database_persistence_across_sessions (test_bmi.TestBMICalculator) ... ok

----------------------------------------------------------------------
Ran 16 tests in 2.915s

OK (16/16 tests passed, 0 failures, 0 errors)
```

---

## 🔮 Future Enhancements

- [ ] **BMR & TDEE Calculator**: Add Basal Metabolic Rate and daily caloric needs estimator.
- [ ] **Body Fat Percentage Calculator**: Integration using the US Navy tape measurement method.
- [ ] **PDF Health Report Generator**: Export professional summary reports with charts and statistics using `reportlab`.
- [ ] **User Authentication**: Optional PIN or password protection for private multi-user profiles.

---

## ⚠️ Medical Disclaimer

> **IMPORTANT**: The Advanced BMI Calculator is developed strictly for **educational and informational purposes**. Body Mass Index (BMI) is a general statistical screening tool based on height and weight. It does not measure body fat distribution, muscle mass, bone density, or individual clinical health. It is **not** a medical diagnosis and should never replace consultation with a licensed physician or registered dietitian.

---

## 👤 Author & Acknowledgments

- **Developer**: OASIS Infobyte Python Programming Intern
- **Internship Program**: OASIS Infobyte Internship (OIBSIP)
- **Track**: Python Programming
- **Task**: Task 2 — BMI Calculator (Advanced GUI Version)
- **Mentor**: Senior Python Developer / OASIS Infobyte Project Mentor

*Submitted with pride as part of the OASIS Infobyte Python Programming Internship.*
