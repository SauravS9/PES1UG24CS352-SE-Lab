"""Lab 7 - Fuzz testing warranty_claims.py with Hypothesis.

Name: R Saurav Srrinivas
SRN : PES1UG24CS352

Each function is fuzzed in two ways:
  1. Pure random input (any text or None) - the function must never crash.
  2. Structured input that looks almost valid (right separator, odd
     numbers) - the function must not crash AND the result must make sense.

A function signals invalid input by returning None instead of raising.
"""
import math

from hypothesis import given, settings, strategies as st

from warranty_claims import parse_claim, age_average, payable_charge

FUZZ = settings(max_examples=300, deadline=None)

# Numbers written the way a user (or an attacker) might type them,
# including nan, inf, negatives, exponents and plain junk.
number_text = st.one_of(
    st.integers().map(str),
    st.floats(allow_nan=True, allow_infinity=True).map(str),
    st.sampled_from(
        ["", " ", "nan", "-inf", "inf", "1e400", "-0", "abc", "1,5"]
    ),
    st.text(max_size=8),
)


# ----------------------------------------------------------------------
# parse_claim
# ----------------------------------------------------------------------
@FUZZ
@given(st.text() | st.none())
def test_parse_claim_no_crash(s):
    try:
        parse_claim(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"parse_claim crashed on {s!r} with: {e!r}"


@FUZZ
@given(st.text(max_size=20), number_text)
def test_parse_claim_months_are_valid(plan, months):
    s = f"{plan}:{months}"
    try:
        result = parse_claim(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"parse_claim crashed on {s!r} with: {e!r}"
    if result is not None:
        name, age = result
        assert name.strip() != "", f"empty plan name accepted for {s!r}"
        assert math.isfinite(age), f"non-finite age {age!r} accepted for {s!r}"
        assert age >= 0, f"negative age {age!r} accepted for {s!r}"


@FUZZ
@given(
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=15),
    st.integers(min_value=0, max_value=600),
)
def test_parse_claim_valid_input(plan, months):
    s = f"{plan}:{months}"
    result = parse_claim(s)
    assert result == (plan.title(), float(months)), \
        f"{s!r} parsed as {result!r}"


# ----------------------------------------------------------------------
# age_average
# ----------------------------------------------------------------------
@FUZZ
@given(st.text() | st.none())
def test_age_average_no_crash(s):
    try:
        age_average(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"age_average crashed on {s!r} with: {e!r}"


@FUZZ
@given(st.lists(st.integers(min_value=-10**6, max_value=10**6), max_size=10))
def test_age_average_csv_lists(ages):
    s = ",".join(str(a) for a in ages)
    try:
        result = age_average(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"age_average crashed on {s!r} with: {e!r}"
    if result is not None:
        assert ages, f"average returned for empty input {s!r}"
        assert min(ages) >= 0, f"negative age accepted in {s!r}"
        assert min(ages) <= result <= max(ages), \
            f"{result} outside range for {s!r}"


@FUZZ
@given(st.lists(st.integers(min_value=0, max_value=1200),
                min_size=1, max_size=20))
def test_age_average_valid_input(ages):
    s = ",".join(str(a) for a in ages)
    result = age_average(s)
    expected = sum(ages) / len(ages)
    assert result is not None, f"valid input {s!r} rejected"
    assert math.isclose(result, expected, abs_tol=0.005), \
        f"average of {s!r} is {expected}, got {result}"


# ----------------------------------------------------------------------
# payable_charge
# ----------------------------------------------------------------------
@FUZZ
@given(st.text() | st.none())
def test_payable_charge_no_crash(s):
    try:
        payable_charge(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"payable_charge crashed on {s!r} with: {e!r}"


@FUZZ
@given(number_text, number_text)
def test_payable_charge_result_is_sane(charge, discount):
    s = f"{charge}|{discount}"
    try:
        result = payable_charge(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"payable_charge crashed on {s!r} with: {e!r}"
    if result is not None:
        assert math.isfinite(result), f"non-finite charge {result!r} for {s!r}"
        assert result >= 0, f"negative charge {result!r} for {s!r}"
        assert float(discount) >= 0, f"negative discount accepted in {s!r}"


@FUZZ
@given(
    st.floats(min_value=0, max_value=1e6, allow_nan=False),
    st.floats(min_value=0, max_value=1e6, allow_nan=False),
)
def test_payable_charge_valid_input(charge, discount):
    s = f"{charge}|{discount}"
    result = payable_charge(s)
    expected = max(charge * 1.18 - discount, 0)
    assert result is not None, f"valid input {s!r} rejected"
    assert math.isclose(result, expected, abs_tol=0.01), \
        f"charge for {s!r} should be {expected}, got {result}"
