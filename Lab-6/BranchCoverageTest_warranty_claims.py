# Lab 6 - Branch Coverage Test Cases
# Name : R Saurav Srrinivas
# SRN  : PES1UG24CS352
# Repo : L6_L7_43_warranty_claims
#
# Goal: make every decision (if / elif / and) in warranty_claims.py
# evaluate to BOTH True and False at least once.
# Run with:
#   coverage run --branch -m pytest BranchCoverageTest_warranty_claims.py
#   coverage report -m

import pytest
from warranty_claims import out_of_warranty_charge, claim_allowed, sla_status


# ======================================================================
# out_of_warranty_charge(plan, age_months, claim_type, is_registered)
# ======================================================================

# --- Branch 1: plan not in COVERED_MONTHS (True / False) ---
def test_unknown_plan_raises():
    with pytest.raises(ValueError, match="unknown plan"):
        out_of_warranty_charge("gold", 10, "defect", False)


def test_known_plan_passes_check():
    assert out_of_warranty_charge("premium", 10, "defect", False) == 0


# --- Branch 2: age_months < 0 (True / False, boundary 0) ---
def test_negative_age_raises():
    with pytest.raises(ValueError, match="invalid age"):
        out_of_warranty_charge("basic", -1, "defect", False)


def test_zero_age_is_valid():
    assert out_of_warranty_charge("basic", 0, "defect", False) == 0


# --- Branch 3: is_registered and plan != "premium" ---
def test_registered_non_premium_gets_extension():
    # basic 12 + 6 = 18 months covered
    assert out_of_warranty_charge("basic", 18, "defect", True) == 0


def test_registered_premium_gets_no_extension():
    # premium stays at 36 -> 40 months => excess 4 * 100
    assert out_of_warranty_charge("premium", 40, "defect", True) == 400


def test_unregistered_no_extension():
    # basic 12, 18 months => excess 6 * 100
    assert out_of_warranty_charge("basic", 18, "defect", False) == 600


# --- Branch 4: excess <= 0 (True / False, boundary) ---
def test_within_warranty():
    assert out_of_warranty_charge("standard", 20, "defect", False) == 0


def test_exactly_at_coverage_limit():
    assert out_of_warranty_charge("standard", 24, "defect", False) == 0


def test_one_month_over_limit():
    assert out_of_warranty_charge("standard", 25, "defect", False) == 100


# --- Branch 5: claim_type == "accidental" (True / False) ---
def test_accidental_small_excess():
    # basic, 15 -> excess 3 * 200
    assert out_of_warranty_charge("basic", 15, "accidental", False) == 600


def test_defect_small_excess():
    assert out_of_warranty_charge("basic", 15, "defect", False) == 300


# --- Branch 6: excess > 12 (True / False, boundary 12) ---
def test_excess_exactly_12_no_surcharge():
    # basic, 24 -> excess 12 * 100
    assert out_of_warranty_charge("basic", 24, "defect", False) == 1200


def test_defect_large_excess_surcharge_only():
    # basic, 25 -> excess 13 * (100 + 50)  (inner accidental check False)
    assert out_of_warranty_charge("basic", 25, "defect", False) == 13 * 150


# --- Branch 7: nested claim_type == "accidental" inside excess > 12 ---
def test_accidental_large_excess_full_surcharge():
    # basic, 30 -> excess 18 * (200 + 50 + 25)
    assert out_of_warranty_charge("basic", 30, "accidental", False) == 18 * 275


# ======================================================================
# claim_allowed(days_since_last_claim, claims_filed, is_recall)
# ======================================================================

def test_claim_allowed():
    assert claim_allowed(60, 1, False) is True


def test_recall_within_limit():
    assert claim_allowed(5, 5, True) is True


def test_recall_over_limit():
    assert claim_allowed(5, 6, True) is False


def test_claim_too_soon():
    assert claim_allowed(29, 0, False) is False


def test_claim_exactly_30_days():
    assert claim_allowed(30, 2, False) is True


def test_too_many_claims():
    assert claim_allowed(45, 3, False) is False


# ======================================================================
# sla_status(hours_left, is_hardware, is_priority)
# ======================================================================

# hardware, non-priority -> cutoff 48
def test_hardware_on_track():
    assert sla_status(48, True, False) == "on_track"


def test_hardware_at_risk():
    assert sla_status(36, True, False) == "at_risk"


def test_hardware_critical():
    assert sla_status(35, True, False) == "critical"


# software, non-priority -> cutoff 24
def test_software_on_track():
    assert sla_status(30, False, False) == "on_track"


def test_software_at_risk():
    assert sla_status(12, False, False) == "at_risk"


def test_software_critical():
    assert sla_status(11, False, False) == "critical"


# priority adds 24 hours
def test_hardware_priority_on_track():
    assert sla_status(72, True, True) == "on_track"


def test_hardware_priority_at_risk():
    assert sla_status(60, True, True) == "at_risk"


def test_software_priority_critical():
    assert sla_status(5, False, True) == "critical"
