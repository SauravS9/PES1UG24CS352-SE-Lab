# L6_L7_43 — Warranty Claims

Lab 7: Fuzzing for Input Validation Bugs

## About

A small Python module that parses warranty claims, averages product ages and works out the payable repair charge after a discount. The three functions were fuzzed with Hypothesis, the bugs it found were fixed, and the tests were re-run.

## Submission

- **Name:** R Saurav Srrinivas
- **SRN:** PES1UG24CS352

| # | Deliverable | File |
|---|-------------|------|
| 1 | PDF document with the screenshots | `PES1UG24CS352_Lab7_FuzzTesting.pdf` |
| 2 | Fixed application Python script | `warranty_claims.py` |
| 3 | Updated Hypothesis test file | `test_warranty_claims.py` |

Other files:

| File | Description |
|------|-------------|
| `warranty_claims_original.py` | The buggy script as given, kept for comparison |
| `screenshots/` | The five screenshots used in the PDF (Steps 2, 4, 5 and 6) |

## How to run

```bash
pip install hypothesis pytest
python warranty_claims.py
python -m pytest test_warranty_claims.py -v
```

## Results

**Before the fix:** 7 of 9 tests failed (`7 failed, 2 passed`).

**After the fix:** all 9 tests pass (`9 passed`). The suite also passes with 5,000 examples per test.

## Bugs found by fuzzing

| Function | Failing input | Problem | Fix |
|----------|---------------|---------|-----|
| all three | `None` | `AttributeError` on `.split()` | Return `None` if the input is not a string |
| all three | `''`, `'::0'`, `'\|'` | Wrong number of parts after split raises `ValueError` | Check the split gives exactly 2 parts |
| `parse_claim` | `':'`, `':0'` | Empty month crashes `float()`; empty plan name accepted | Plan must contain a letter or digit and only letters, digits, space, `-` or `_` |
| `parse_claim` | `'0:nan'`, `'0:-1'` | `nan`, `inf` and negative months accepted | Months must be finite and `>= 0` |
| `age_average` | `''` | `int('')` raises; an empty list would divide by zero | Reject blank input and any token that is not a whole number |
| `age_average` | `'-1'` | Negative ages accepted | Reject ages below 0 |
| `age_average` | `'0,1'` | Floor division gives `0` instead of `0.5` | True division rounded to 2 places; `OverflowError` caught |
| `payable_charge` | `'0\|'` | Empty number crashes `float()` | Parse each side safely |
| `payable_charge` | `'0\|nan'` | `max(nan, 0)` returns `nan` as the charge | Charge and discount must be finite and `>= 0`; total must be finite |
| `payable_charge` | `'0\|-1'` | A negative discount increases the bill | Reject negative discounts; result rounded to 2 places |
| `main` | any bad line | One bad value crashes the whole program | Print an "Invalid input" message and continue; EOF on input is handled |

Each function now returns `None` for input it cannot use instead of raising an exception.
