"""Warranty claims module - hardened against invalid input (Lab 7).

Name: R Saurav Srrinivas
SRN : PES1UG24CS352

Every public function validates its input and returns None for anything
it cannot handle, instead of raising an exception or returning nonsense
such as nan, inf or a negative amount.
"""
import math

GST_MULTIPLIER = 1.18
ALLOWED_PLAN_CHARS = " -_"


def _to_number(token):
    """Convert text to a finite, non-negative float, or return None."""
    try:
        value = float(token)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(value) or value < 0:
        return None
    return value


def _valid_plan(name):
    """A plan name must contain a letter or digit and nothing unusual."""
    return any(c.isalnum() for c in name) and all(
        c.isalnum() or c in ALLOWED_PLAN_CHARS for c in name
    )


def parse_claim(text):
    """Parse 'plan:months' into (Plan, months) or return None if invalid."""
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    plan = parts[0].strip()
    months = _to_number(parts[1].strip())
    if not _valid_plan(plan) or months is None:
        return None
    return plan.title(), months


def age_average(ages_csv):
    """Average of comma-separated whole-month ages, or None if invalid."""
    if not isinstance(ages_csv, str) or not ages_csv.strip():
        return None
    values = []
    for token in ages_csv.split(','):
        try:
            value = int(token.strip())
        except ValueError:
            return None
        if value < 0:
            return None
        values.append(value)
    try:
        return round(sum(values) / len(values), 2)
    except OverflowError:
        return None


def payable_charge(text):
    """Charge with 18% GST minus discount, floored at 0, or None if invalid."""
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    charge = _to_number(parts[0].strip())
    discount = _to_number(parts[1].strip())
    if charge is None or discount is None:
        return None
    total = charge * GST_MULTIPLIER - discount
    if not math.isfinite(total):
        return None
    return round(max(total, 0.0), 2)


def _read(prompt):
    """input() that returns an empty string instead of failing on EOF."""
    try:
        return input(prompt)
    except EOFError:
        return ""


def _show(label, result, hint):
    """Print the result, or a friendly message when the input was invalid."""
    if result is None:
        print(f"Invalid input. {hint}")
    else:
        print(f"{label}:", result)


def main():
    """Read one input for each function and print the results."""
    print("==== Running parse_claim ====")
    user_input = _read("Enter plan:age in months (e.g. standard:30): ")
    _show("Plan and Age", parse_claim(user_input),
          "Use plan:months with a plan name and a non-negative number.")

    print("\n==== Running age_average ====")
    user_input = _read("Enter product ages as CSV (e.g. 12,24,36): ")
    _show("Average Age", age_average(user_input),
          "Use comma-separated non-negative whole numbers.")

    print("\n==== Running payable_charge ====")
    user_input = _read("Enter charge|discount (e.g. 1500|200): ")
    _show("Payable Charge", payable_charge(user_input),
          "Use charge|discount with two non-negative numbers.")


if __name__ == "__main__":
    main()
