# Lab 5: Static Code Analysis — Issue Table

**Name:** R Saurav Srrinivas
**SRN:** PES1UG24CS352
**Repo:** L5_43_hotel_booking_system
**File:** `hotel_booking_system.py`

## Summary

| Tool   | Before | After |
|--------|--------|-------|
| Pylint | 5.32 / 10 | **10.00 / 10** |
| Bandit | 6 issues (2 High, 1 Medium, 3 Low) | **No issues identified** |
| Flake8 | 7 issues | **0 issues** |

Reports: `reports/before/` and `reports/after/` (`pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt`).

## Issues found and fixed

Line numbers refer to the **original** file. Sorted by severity, high and medium first.

| # | Issue | Type | Tool / Code | Severity | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|----------|---------|-------------|--------------|
| 1 | Shell command injection | Security | Bandit B605 | High | 58 | `os.system("echo ... " + filename)` passes the filename to a shell. A name like `x; rm -rf ~` would run extra commands. | Removed the shell call. The message is printed with `print()`. |
| 2 | Weak hash (MD5) | Security | Bandit B324 | High | 47 | MD5 is broken and easy to brute-force, so guest IDs could be recovered from the hash. | Switched to `hashlib.sha256`. |
| 3 | Use of `eval()` | Security | Bandit B307, Pylint W0123 | Medium | 42 | `eval(rate_expr)` runs any Python code passed in as a string (arbitrary code execution). | Changed the parameter to a numeric `surge_multiplier`: `base_price * float(surge_multiplier)`. Invalid values now raise `ValueError`. |
| 4 | Mutable default argument | Bug | Pylint W0102 | Medium | 15 | `booking_log=[]` is created once and shared across every call, so log entries leak between calls. | Default changed to `None`; a new list is created inside the function. |
| 5 | Bare `except` with `pass` | Bug / Security | Bandit B110, Flake8 E722, Pylint W0702 | Medium | 26–27 | Catches every exception (even `KeyboardInterrupt`) and hides it. Cancelling a non-existent room failed silently. | Catch only the expected case and return `False` with a message (later rewritten to an explicit existence check). |
| 6 | Hardcoded secret, printed to console | Security | Bandit B105 | Low (real impact high) | 62, 70 | The admin token is stored in source code (ends up on GitHub) and printed to stdout. | Read from the `HOTEL_SECRET_KEY` environment variable; only print whether it is configured, never the value. |
| 7 | Insecure random generator | Security | Bandit B311 | Low | 51 | `random` is predictable, so booking references could be guessed. | Used `secrets.randbelow(9000) + 1000`. |
| 8 | File opened without `with` / encoding | Quality | Pylint R1732, W1514 | Medium | 55–57 | If `write()` raises, the file is never closed; the encoding depends on the OS. | `with open(filename, "w", encoding="utf-8")`. |
| 9 | Non-snake_case function name | Style | Pylint C0103 | Low | 15 | `bookRoom` breaks PEP 8 naming. | Renamed to `book_room` (and updated the call in `main`). |
| 10 | Unused variables | Quality | Flake8 F841, Pylint W0612 | Low | 31, 41 | `cleaning_deposit` was never used; `base_price` was unused because the price went through `eval`. | Removed `cleaning_deposit`; `base_price` is now used in the calculation. |
| 11 | Unused import | Style | Flake8 F401, Pylint W0611 | Low | 6 | `math` was imported but never used. | Removed the import. |
| 12 | `== None` comparison | Style | Flake8 E711, Pylint C0121 | Low | 32 | `None` should be compared by identity. | Changed to `is None`. |
| 13 | Redundant if/else | Quality | Pylint R1703, R1705 | Low | 34–37 | `if ...: return True else: return False`. | Replaced with `return not room_inventory[room_num]["is_booked"]`. |
| 14 | Missing docstrings | Documentation | Pylint C0116 | Low | 15, 23, 30, 40, 46, 50, 54, 61 | No function documented its purpose or return value. | Added a docstring to every function. |
| 15 | %-formatting | Style | Pylint C0209 | Low | 19 | Old-style string formatting. | Converted to an f-string. |
| 16 | Line too long | Style | Flake8 E501 | Low | 19 | 80 characters (limit 79). | Wrapped the line in the Flake8 commit; it was later shortened further by the f-string change. |
| 17 | No final newline | Style | Flake8 W292, Pylint C0304 | Low | 73 | File did not end with a newline. | Added a trailing newline. |
| 18 | `main()` runs on import | Quality | (manual review) | Medium | 73 | Calling `main()` at module level means `import hotel_booking_system` books and cancels rooms and writes files. | Wrapped in `if __name__ == "__main__":`. |

## Logic bugs no tool reported (found by running the program and reviewing the code)

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 19 | Cancelling an unbooked room "succeeds" | Logic bug | 23–27 | `cancel_booking` set `is_booked = False` without checking whether the room was booked, and gave no result. | Return `False` with a message if the room doesn't exist or isn't booked; return `True` only when a booking is released. |
| 20 | Floating-point price errors / invalid surge | Logic bug | 40–43 | `90 * 1.15` gives `103.49999999999999`. Zero or negative multipliers produced invalid prices, and unknown rooms crashed with a raw `KeyError`. | Round to 2 decimals; raise `ValueError` for multiplier ≤ 0 and a clear `KeyError` for unknown rooms. |
| 21 | Ledger not machine-readable | Logic bug | 56 | `str(room_inventory)` writes a Python repr (`True`, single quotes), not a parseable format. | Export with `json.dump(..., indent=2)`. |
| 22 | Results silently discarded | Logic bug | 63–64 | `main` ignored the return values of booking/cancelling, and the booking log was never kept or shown. | `main` passes its own `booking_log` list and prints each result and the log. |

## Verification

```
$ pylint hotel_booking_system.py
Your code has been rated at 10.00/10

$ bandit -r hotel_booking_system.py
Test results:
        No issues identified.

$ flake8 hotel_booking_system.py
(no output)

$ python hotel_booking_system.py
Book 101: True
Cancel 102: True
Is 103 available: True
Surge price: 187.5
Guest Hash: 6d7f221fa359b1754599b3aa07ca54f52b4e136267d3e3b505fc5d64df61100d
Booking Reference: <random 4-digit number>
Booking log: ['Reserved room 101 for guest Emma Watson']
Hotel ledger exported to: hotel_ledger.txt
Secret key configured: False
```
