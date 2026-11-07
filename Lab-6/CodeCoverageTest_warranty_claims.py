# Lab 6 - Code (Line) Coverage Test Cases
# Name : R Saurav Srrinivas
# SRN  : PES1UG24CS352
# Repo : L6_L7_43_warranty_claims
#
# Goal: execute every line of warranty_claims.py at least once.
# Run with:
#   coverage run -m pytest CodeCoverageTest_warranty_claims.py
#   coverage report -m

import pytest
from warranty_claims import out_of_warranty_charge, claim_allowed, sla_status


# ---------------- out_of_warranty_charge ----------------

def test_within_warranty():
    # standard plan, 20 months old -> still inside 24 months
    assert out_of_warranty_charge("standard", 20, "defect", False) == 0


def test_unknown_plan_raises():
    with pytest.raises(ValueError, match="unknown plan"):
        out_of_warranty_charge("gold", 10, "defect", False)


def test_negative_age_raises():
    with pytest.raises(ValueError, match="invalid age"):
        out_of_warranty_charge("basic", -1, "defect", False)


def test_registered_extension_keeps_claim_free():
    # basic (12) + 6 months registration bonus = 18 -> 16 months is covered
    assert out_of_warranty_charge("basic", 16, "defect", True) == 0


def test_defect_small_excess():
    # basic, 15 months -> excess 3, rate 100
    assert out_of_warranty_charge("basic", 15, "defect", False) == 300


def test_accidental_large_excess():
    # basic, 30 months -> excess 18 (>12), rate 200 + 50 + 25 = 275
    assert out_of_warranty_charge("basic", 30, "accidental", False) == 18 * 275


# ---------------- claim_allowed ----------------

def test_claim_allowed():
    assert claim_allowed(60, 1, False) is True


def test_recall_claim():
    assert claim_allowed(5, 4, True) is True


def test_claim_too_soon():
    assert claim_allowed(10, 0, False) is False


# ---------------- sla_status ----------------

def test_sla_hardware_priority_on_track():
    # hardware 48 + priority 24 = 72
    assert sla_status(80, True, True) == "on_track"


def test_sla_software_at_risk():
    # software 24 + priority 24 = 48 ; 40 is within the 12h window
    assert sla_status(40, False, True) == "at_risk"


def test_sla_critical():
    assert sla_status(5, False, True) == "critical"
