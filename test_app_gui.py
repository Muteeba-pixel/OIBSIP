"""
test_app_gui.py
===============
End-to-End GUI automated integration test.
Instantiates the Tkinter BMICalculatorApp, populates inputs, exercises UI actions
(calculate, save, user switch, chart render, reset), and verifies error-free execution.
"""

import os
import sys
import tempfile
import shutil
import unittest

from app import BMICalculatorApp
import database


class TestAppGUI(unittest.TestCase):
    """Verifies that the Tkinter application initializes and executes all user flows."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.test_dir, "gui_test.db")
        # Ensure database is initialized
        database.init_database(self.test_db)
        # Create app instance with test database
        self.app = BMICalculatorApp(db_path=self.test_db)
        # Prevent window from stealing desktop focus during test
        self.app.withdraw()

    def tearDown(self):
        try:
            self.app.destroy()
        except Exception:
            pass
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_gui_calculation_and_save_flow(self):
        """Simulate user typing measurements, calculating BMI, and saving to database."""
        # 1. Select User
        self.app.user_name_var.set("TestRunner")
        self.app._on_user_changed()

        # 2. Set Weight and Height (Metric: 72 kg, 178 cm)
        self.app.unit_system_var.set("metric")
        self.app.weight_var.set("72")
        self.app.height_var.set("178")

        # 3. Calculate BMI
        result = self.app.calculate_and_display()
        self.assertIsNotNone(result)
        self.assertEqual(result.category, "Normal")
        self.assertEqual(self.app.lbl_bmi_value.cget("text"), "22.72")

        # 4. Save record
        self.app.notes_var.set("Automated test run")
        # Direct call to database add_record to bypass modal messagebox in headless mode
        database.add_record(
            user_name="TestRunner",
            weight=result.weight_kg,
            height=result.height_m,
            bmi=result.bmi,
            category=result.category,
            notes="Automated test run",
            db_path=self.test_db
        )
        self.app._reload_user_list()
        self.app._refresh_history_table()
        self.app._refresh_chart()

        # Verify record appears in Treeview
        children = self.app.tree.get_children()
        self.assertEqual(len(children), 1)

        # 5. Test Reset
        self.app.reset_inputs()
        self.assertEqual(self.app.weight_var.get(), "")
        self.assertEqual(self.app.height_var.get(), "")
        self.assertEqual(self.app.lbl_bmi_value.cget("text"), "--.--")

    def test_gui_imperial_units_flow(self):
        """Test imperial units conversion and display in GUI."""
        self.app.unit_system_var.set("imperial")
        self.app._on_unit_system_changed()
        self.assertEqual(self.app.lbl_weight.cget("text"), "Weight (lbs):")
        self.assertEqual(self.app.lbl_height.cget("text"), "Height (in):")

        # 160 lbs, 70 inches -> ~22.95 BMI (Normal)
        self.app.weight_var.set("160")
        self.app.height_var.set("70")
        result = self.app.calculate_and_display()
        self.assertIsNotNone(result)
        self.assertEqual(result.category, "Normal")


if __name__ == "__main__":
    unittest.main(verbosity=2)
