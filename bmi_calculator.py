"""
bmi_calculator.py
=================
Core computational and validation logic for the Advanced BMI Calculator.

OASIS Infobyte Python Programming Internship - Task 2
Author: OASIS Intern / Python Developer
"""

from dataclasses import dataclass
from typing import Optional, Tuple


class BMIValidationError(ValueError):
    """Custom exception raised when user inputs fail numerical or logical validation."""
    pass


@dataclass
class BMIResult:
    """Encapsulates the complete result of a BMI calculation."""
    bmi: float
    category: str
    color_hex: str
    min_healthy_weight: float
    max_healthy_weight: float
    weight_difference: float
    recommendation: str
    weight_kg: float
    height_m: float

    @property
    def bmi_formatted(self) -> str:
        """Return BMI rounded to 2 decimal places."""
        return f"{self.bmi:.2f}"

    @property
    def healthy_range_formatted(self) -> str:
        """Formatted healthy weight range string in kg."""
        return f"{self.min_healthy_weight:.1f} kg - {self.max_healthy_weight:.1f} kg"


# BMI Category definitions and color styling
CATEGORY_UNDERWEIGHT = "Underweight"
CATEGORY_NORMAL = "Normal"
CATEGORY_OVERWEIGHT = "Overweight"
CATEGORY_OBESE = "Obese"

CATEGORY_COLORS = {
    CATEGORY_UNDERWEIGHT: "#0284c7",  # Sky Blue
    CATEGORY_NORMAL: "#16a34a",       # Vibrant Green
    CATEGORY_OVERWEIGHT: "#d97706",   # Amber / Orange
    CATEGORY_OBESE: "#dc2626",        # Crimson Red
}

CATEGORY_THRESHOLDS = [
    (18.5, CATEGORY_UNDERWEIGHT),
    (24.9, CATEGORY_NORMAL),
    (29.9, CATEGORY_OVERWEIGHT),
]


def classify_bmi(bmi: float) -> Tuple[str, str]:
    """
    Classify a calculated BMI value according to standard WHO guidelines.

    Categories:
        - Underweight: BMI < 18.5
        - Normal:      BMI 18.5 – 24.9
        - Overweight:  BMI 25.0 – 29.9
        - Obese:       BMI >= 30.0

    Returns:
        Tuple of (category_name, hex_color_code)
    """
    if bmi < 18.5:
        category = CATEGORY_UNDERWEIGHT
    elif bmi <= 24.99:
        category = CATEGORY_NORMAL
    elif bmi <= 29.99:
        category = CATEGORY_OVERWEIGHT
    else:
        category = CATEGORY_OBESE

    return category, CATEGORY_COLORS[category]


def validate_inputs(
    weight_raw: str,
    height_raw: str,
    unit_system: str = "metric",
    user_name: Optional[str] = None
) -> Tuple[float, float, str]:
    """
    Validate raw inputs from the user interface.

    Checks performed:
        - Non-empty values
        - Clean user name
        - Numeric parsing
        - Non-zero values
        - Non-negative values
        - Biologically plausible ranges

    Args:
        weight_raw: Raw weight string from input
        height_raw: Raw height string from input
        unit_system: 'metric' (kg, cm/m) or 'imperial' (lbs, inches)
        user_name: Optional user name string

    Returns:
        Tuple of (weight_kg, height_m, cleaned_user_name)

    Raises:
        BMIValidationError: If any input fails validation with a user-friendly message.
    """
    # 1. Validate User Name
    if user_name is not None:
        cleaned_name = user_name.strip()
        if not cleaned_name:
            raise BMIValidationError("Please enter a valid user name.")
        if len(cleaned_name) > 50:
            raise BMIValidationError("User name cannot exceed 50 characters.")
    else:
        cleaned_name = "Default User"

    # 2. Check Empty Inputs
    if not str(weight_raw).strip():
        raise BMIValidationError("Weight field cannot be empty. Please enter your weight.")
    if not str(height_raw).strip():
        raise BMIValidationError("Height field cannot be empty. Please enter your height.")

    # 3. Numeric Parse Checks
    try:
        weight_val = float(weight_raw)
    except (ValueError, TypeError):
        raise BMIValidationError("Weight must be a valid number (e.g., 70 or 68.5).")

    try:
        height_val = float(height_raw)
    except (ValueError, TypeError):
        raise BMIValidationError("Height must be a valid number (e.g., 175 or 1.75).")

    # 4. Non-zero and Non-negative Checks
    if weight_val <= 0:
        raise BMIValidationError("Weight must be greater than zero. Negative or zero weight is invalid.")
    if height_val <= 0:
        raise BMIValidationError("Height must be greater than zero. Negative or zero height is invalid.")

    # 5. Unit Conversion and Plausible Range Checks
    unit_norm = unit_system.strip().lower()

    if unit_norm == "metric":
        # Weight in kg
        weight_kg = weight_val
        if weight_kg < 10.0 or weight_kg > 450.0:
            raise BMIValidationError(
                f"Weight of {weight_kg:.1f} kg is outside the plausible range (10 - 450 kg)."
            )

        # Height can be provided in centimeters (> 3) or meters (<= 3)
        if height_val > 3.0:
            # Entered in centimeters (e.g., 175 cm)
            height_m = height_val / 100.0
        else:
            # Entered in meters (e.g., 1.75 m)
            height_m = height_val

        if height_m < 0.50 or height_m > 2.60:
            raise BMIValidationError(
                f"Height of {height_val} ({height_m:.2f} m) is outside plausible range (0.50 m - 2.60 m / 50 cm - 260 cm)."
            )

    elif unit_norm == "imperial":
        # Weight in lbs -> convert to kg (1 lb = 0.45359237 kg)
        if weight_val < 22.0 or weight_val > 1000.0:
            raise BMIValidationError(
                f"Weight of {weight_val:.1f} lbs is outside the plausible range (22 - 1000 lbs)."
            )
        weight_kg = weight_val * 0.45359237

        # Height in inches -> convert to meters (1 in = 0.0254 m)
        if height_val < 20.0 or height_val > 105.0:
            raise BMIValidationError(
                f"Height of {height_val:.1f} inches is outside the plausible range (20 - 105 inches)."
            )
        height_m = height_val * 0.0254

    else:
        raise BMIValidationError(f"Unsupported unit system: '{unit_system}'. Use 'metric' or 'imperial'.")

    return weight_kg, height_m, cleaned_name


def calculate_bmi(
    weight_raw: str,
    height_raw: str,
    unit_system: str = "metric",
    user_name: Optional[str] = None
) -> BMIResult:
    """
    Validate inputs and calculate BMI with category and health recommendations.

    Formula:
        BMI = weight (kg) / (height (m) ** 2)

    Returns:
        BMIResult dataclass containing calculated metrics.
    """
    weight_kg, height_m, _ = validate_inputs(
        weight_raw=weight_raw,
        height_raw=height_raw,
        unit_system=unit_system,
        user_name=user_name
    )

    # Core mathematical formula: BMI = weight / (height ** 2)
    bmi = weight_kg / (height_m ** 2)
    bmi_rounded = round(bmi, 2)

    category, color_hex = classify_bmi(bmi_rounded)

    # Calculate healthy weight range for this specific height (BMI 18.5 - 24.9)
    min_healthy_weight = round(18.5 * (height_m ** 2), 2)
    max_healthy_weight = round(24.9 * (height_m ** 2), 2)

    # Calculate difference to healthy range
    if bmi_rounded < 18.5:
        diff = round(min_healthy_weight - weight_kg, 1)
        rec = f"You are underweight. Consider gaining approx. {diff} kg to reach normal BMI."
    elif bmi_rounded > 24.99:
        diff = round(weight_kg - max_healthy_weight, 1)
        rec = f"You are in the {category.lower()} range. Consider losing approx. {diff} kg to reach normal BMI."
    else:
        diff = 0.0
        rec = "Congratulations! Your weight is in the healthy/normal range for your height."

    return BMIResult(
        bmi=bmi_rounded,
        category=category,
        color_hex=color_hex,
        min_healthy_weight=min_healthy_weight,
        max_healthy_weight=max_healthy_weight,
        weight_difference=diff,
        recommendation=rec,
        weight_kg=round(weight_kg, 2),
        height_m=round(height_m, 2)
    )
