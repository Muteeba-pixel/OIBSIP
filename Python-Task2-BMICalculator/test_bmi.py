"""
test_bmi.py
===========
Automated Test Suite for Advanced BMI Calculator & Health Tracker.

Tests all 13 core requirements specified by OASIS Infobyte:
1. Valid Normal BMI
2. Underweight BMI
3. Overweight BMI
4. Obese BMI
5. Empty input validation
6. Text/Non-numeric input validation
7. Zero value validation
8. Negative value validation
9. Saving a record to SQLite
10. Loading history from SQLite
11. Multiple users isolation
12. Matplotlib BMI trend chart generation (0, 1, and multiple points)
13. Database error handling under adverse conditions

Run via:
    python -m unittest test_bmi.py -v
"""

import os
import unittest
import tempfile
import shutil
from matplotlib.figure import Figure

from bmi_calculator import (
    calculate_bmi,
    classify_bmi,
    validate_inputs,
    BMIValidationError,
    CATEGORY_UNDERWEIGHT,
    CATEGORY_NORMAL,
    CATEGORY_OVERWEIGHT,
    CATEGORY_OBESE
)
import database
import chart


class TestBMICalculator(unittest.TestCase):
    """Test suite covering calculation logic, validation, persistence, and charting."""

    def setUp(self):
        """Create a temporary directory and database for isolated testing."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.test_dir, "test_bmi.db")
        database.init_database(self.test_db)

    def tearDown(self):
        """Clean up temporary directory and database."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # --------------------------------------------------------------------------
    # 1. Valid Normal BMI Test
    # --------------------------------------------------------------------------
    def test_01_normal_bmi(self):
        """Verify normal BMI calculation and classification (18.5 - 24.9)."""
        # 70 kg, 175 cm (1.75 m) -> 70 / (1.75^2) = 22.857... -> 22.86
        result = calculate_bmi("70", "175", unit_system="metric", user_name="Alice")
        self.assertEqual(result.bmi, 22.86)
        self.assertEqual(result.category, CATEGORY_NORMAL)
        self.assertEqual(result.weight_difference, 0.0)
        self.assertIn("healthy/normal", result.recommendation)

    # --------------------------------------------------------------------------
    # 2. Underweight BMI Test
    # --------------------------------------------------------------------------
    def test_02_underweight_bmi(self):
        """Verify underweight BMI calculation and classification (< 18.5)."""
        # 45 kg, 175 cm (1.75 m) -> 45 / (1.75^2) = 14.69
        result = calculate_bmi("45", "175", unit_system="metric", user_name="Bob")
        self.assertEqual(result.bmi, 14.69)
        self.assertEqual(result.category, CATEGORY_UNDERWEIGHT)
        self.assertGreater(result.weight_difference, 0.0)
        self.assertIn("underweight", result.recommendation.lower())

    # --------------------------------------------------------------------------
    # 3. Overweight BMI Test
    # --------------------------------------------------------------------------
    def test_03_overweight_bmi(self):
        """Verify overweight BMI calculation and classification (25.0 - 29.9)."""
        # 80 kg, 170 cm (1.70 m) -> 80 / (1.70^2) = 27.68
        result = calculate_bmi("80", "170", unit_system="metric", user_name="Charlie")
        self.assertEqual(result.bmi, 27.68)
        self.assertEqual(result.category, CATEGORY_OVERWEIGHT)
        self.assertGreater(result.weight_difference, 0.0)
        self.assertIn("overweight", result.recommendation.lower())

    # --------------------------------------------------------------------------
    # 4. Obese BMI Test
    # --------------------------------------------------------------------------
    def test_04_obese_bmi(self):
        """Verify obese BMI calculation and classification (>= 30.0)."""
        # 105 kg, 170 cm (1.70 m) -> 105 / (1.70^2) = 36.33
        result = calculate_bmi("105", "170", unit_system="metric", user_name="David")
        self.assertEqual(result.bmi, 36.33)
        self.assertEqual(result.category, CATEGORY_OBESE)
        self.assertGreater(result.weight_difference, 0.0)
        self.assertIn("obese", result.recommendation.lower())

    # --------------------------------------------------------------------------
    # 5. Empty Input Validation Test
    # --------------------------------------------------------------------------
    def test_05_empty_inputs(self):
        """Verify that empty weight or height raises BMIValidationError."""
        with self.assertRaises(BMIValidationError) as ctx:
            calculate_bmi("", "175", unit_system="metric")
        self.assertIn("cannot be empty", str(ctx.exception).lower())

        with self.assertRaises(BMIValidationError) as ctx:
            calculate_bmi("70", "", unit_system="metric")
        self.assertIn("cannot be empty", str(ctx.exception).lower())

        with self.assertRaises(BMIValidationError) as ctx:
            calculate_bmi("   ", "   ", unit_system="metric")
        self.assertIn("cannot be empty", str(ctx.exception).lower())

    # --------------------------------------------------------------------------
    # 6. Non-Numeric Input Validation Test
    # --------------------------------------------------------------------------
    def test_06_non_numeric_inputs(self):
        """Verify that alphabetic or special characters raise BMIValidationError."""
        with self.assertRaises(BMIValidationError) as ctx:
            calculate_bmi("seventy", "175", unit_system="metric")
        self.assertIn("must be a valid number", str(ctx.exception).lower())

        with self.assertRaises(BMIValidationError) as ctx:
            calculate_bmi("70", "tall", unit_system="metric")
        self.assertIn("must be a valid number", str(ctx.exception).lower())

        with self.assertRaises(BMIValidationError) as ctx:
            calculate_bmi("@#$", "175", unit_system="metric")
        self.assertIn("must be a valid number", str(ctx.exception).lower())

    # --------------------------------------------------------------------------
    # 7. Zero Value Validation Test
    # --------------------------------------------------------------------------
    def test_07_zero_values(self):
        """Verify that zero weight or height raises BMIValidationError."""
        with self.assertRaises(BMIValidationError) as ctx:
            calculate_bmi("0", "175", unit_system="metric")
        self.assertIn("greater than zero", str(ctx.exception).lower())

        with self.assertRaises(BMIValidationError) as ctx:
            calculate_bmi("70", "0", unit_system="metric")
        self.assertIn("greater than zero", str(ctx.exception).lower())

    # --------------------------------------------------------------------------
    # 8. Negative Value Validation Test
    # --------------------------------------------------------------------------
    def test_08_negative_values(self):
        """Verify that negative weight or height raises BMIValidationError."""
        with self.assertRaises(BMIValidationError) as ctx:
            calculate_bmi("-70", "175", unit_system="metric")
        self.assertIn("greater than zero", str(ctx.exception).lower())

        with self.assertRaises(BMIValidationError) as ctx:
            calculate_bmi("70", "-175", unit_system="metric")
        self.assertIn("greater than zero", str(ctx.exception).lower())

    # --------------------------------------------------------------------------
    # 9. Saving a Record Test
    # --------------------------------------------------------------------------
    def test_09_saving_record(self):
        """Verify that BMI record is correctly persisted to SQLite."""
        row_id = database.add_record(
            user_name="John Doe",
            weight=75.0,
            height=1.80,
            bmi=23.15,
            category=CATEGORY_NORMAL,
            notes="Morning weigh-in",
            db_path=self.test_db
        )
        self.assertIsInstance(row_id, int)
        self.assertGreater(row_id, 0)

        # Retrieve and verify
        records = database.get_user_records("John Doe", db_path=self.test_db)
        self.assertEqual(len(records), 1)
        rec = records[0]
        self.assertEqual(rec["user_name"], "John Doe")
        self.assertEqual(rec["weight"], 75.0)
        self.assertEqual(rec["height"], 1.80)
        self.assertEqual(rec["bmi"], 23.15)
        self.assertEqual(rec["category"], CATEGORY_NORMAL)
        self.assertEqual(rec["notes"], "Morning weigh-in")

    # --------------------------------------------------------------------------
    # 10. Loading History Test
    # --------------------------------------------------------------------------
    def test_10_loading_history(self):
        """Verify historical records query returns correct count and order."""
        database.add_record("Jane", 60.0, 1.65, 22.04, CATEGORY_NORMAL, created_at="2026-01-01 10:00:00", db_path=self.test_db)
        database.add_record("Jane", 62.0, 1.65, 22.77, CATEGORY_NORMAL, created_at="2026-02-01 10:00:00", db_path=self.test_db)
        database.add_record("Jane", 64.0, 1.65, 23.51, CATEGORY_NORMAL, created_at="2026-03-01 10:00:00", db_path=self.test_db)

        # DESC order (newest first)
        desc_records = database.get_user_records("Jane", order="DESC", db_path=self.test_db)
        self.assertEqual(len(desc_records), 3)
        self.assertEqual(desc_records[0]["created_at"], "2026-03-01 10:00:00")
        self.assertEqual(desc_records[2]["created_at"], "2026-01-01 10:00:00")

        # ASC order (oldest first)
        asc_records = database.get_user_records("Jane", order="ASC", db_path=self.test_db)
        self.assertEqual(len(asc_records), 3)
        self.assertEqual(asc_records[0]["created_at"], "2026-01-01 10:00:00")
        self.assertEqual(asc_records[2]["created_at"], "2026-03-01 10:00:00")

    # --------------------------------------------------------------------------
    # 11. Multiple Users Isolation Test
    # --------------------------------------------------------------------------
    def test_11_multiple_users(self):
        """Verify that multiple users have segregated and distinct records."""
        database.add_record("Alice", 55.0, 1.60, 21.48, CATEGORY_NORMAL, db_path=self.test_db)
        database.add_record("Bob", 85.0, 1.75, 27.76, CATEGORY_OVERWEIGHT, db_path=self.test_db)
        database.add_record("Alice", 56.0, 1.60, 21.88, CATEGORY_NORMAL, db_path=self.test_db)

        users = database.get_users(db_path=self.test_db)
        self.assertEqual(users, ["Alice", "Bob"])

        alice_recs = database.get_user_records("Alice", db_path=self.test_db)
        self.assertEqual(len(alice_recs), 2)
        for r in alice_recs:
            self.assertEqual(r["user_name"], "Alice")

        bob_recs = database.get_user_records("Bob", db_path=self.test_db)
        self.assertEqual(len(bob_recs), 1)
        self.assertEqual(bob_recs[0]["user_name"], "Bob")

    # --------------------------------------------------------------------------
    # 12. Matplotlib Trend Chart Generation Test
    # --------------------------------------------------------------------------
    def test_12_bmi_trend_chart(self):
        """Verify trend chart renders cleanly for empty, single, and multiple records."""
        fig = Figure(figsize=(6, 4))

        # Case A: 0 records
        chart.render_bmi_chart(fig, [], "EmptyUser")
        self.assertEqual(len(fig.axes), 1)

        # Case B: 1 record
        single_record = [{
            "bmi": 22.5,
            "category": "Normal",
            "created_at": "2026-05-01 08:30:00"
        }]
        chart.render_bmi_chart(fig, single_record, "SingleUser")
        self.assertEqual(len(fig.axes), 1)

        # Case C: Multiple records
        multi_records = [
            {"bmi": 26.2, "category": "Overweight", "created_at": "2026-01-10 09:00:00"},
            {"bmi": 25.1, "category": "Overweight", "created_at": "2026-02-15 09:00:00"},
            {"bmi": 23.8, "category": "Normal", "created_at": "2026-03-20 09:00:00"},
        ]
        chart.render_bmi_chart(fig, multi_records, "MultiUser")
        self.assertEqual(len(fig.axes), 1)

    # --------------------------------------------------------------------------
    # 13. Database Error Handling Test
    # --------------------------------------------------------------------------
    def test_13_database_error_handling(self):
        """Verify that database errors are caught and raised as DatabaseError."""
        with self.assertRaises(database.DatabaseError):
            database.add_record(
                user_name="",  # Empty username should trigger validation/error
                weight=70.0,
                height=1.75,
                bmi=22.86,
                category="Normal",
                db_path=self.test_db
            )

    # --------------------------------------------------------------------------
    # 14. Database Persistence Across Sessions Test
    # --------------------------------------------------------------------------
    def test_14_database_persistence_across_sessions(self):
        """Verify that saved records remain intact after connection close and app restart."""
        # Session 1: Add records
        database.add_record("SessionUser", 68.0, 1.72, 22.99, CATEGORY_NORMAL, notes="Session 1", db_path=self.test_db)
        
        # Session 2: Fresh query simulating app restart
        records = database.get_user_records("SessionUser", db_path=self.test_db)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["notes"], "Session 1")
        self.assertEqual(records[0]["bmi"], 22.99)
        self.assertEqual(records[0]["category"], CATEGORY_NORMAL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
