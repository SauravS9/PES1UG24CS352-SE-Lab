# Lab 5: Static Code Analysis — Reflection

**Name:** R Saurav Srrinivas
**SRN:** PES1UG24CS352
**Repo:** L5_43_hotel_booking_system

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

**Easiest:** the Flake8 style issues and simple Pylint warnings: the unused `math` import, the unused `cleaning_deposit` variable, `== None` → `is None`, the missing final newline, the long line and the missing docstrings. Each one has a single obvious fix that doesn't change what the program does.

**Hardest:** `eval(rate_expr)` (B307) and the hardcoded secret (B105). Removing `eval` meant changing the function's interface: it used to take an expression string and now takes a number, so the caller had to change too, and I had to decide how to handle bad input (zero, negative or unknown room). For the secret, I couldn't just delete the string. I had to move it out of the code (into the `HOTEL_SECRET_KEY` environment variable) and also stop printing it, because printing it leaked it just as badly as hardcoding it. The bare `except: pass` was also tricky: once it no longer swallowed errors, it became clear that `cancel_booking` had a logic bug (it "cancelled" rooms that weren't booked).

### 2. Did the static analysis tools report any false positives? If so, describe one example.

Partly. **B311** (insecure `random` for booking references) is a borderline case. A 4-digit booking reference isn't a password or a crypto key, so in a small demo `random` is acceptable. I still fixed it with `secrets`, because guessable references could let someone look up another guest's booking. **B105** (hardcoded password) is a heuristic: Bandit flags it because the variable name contains "secret"/"key" and is assigned a string literal, and it would also flag harmless strings with similar names. Here, though, the finding was real.

The more important lesson is the opposite: **false negatives**. No tool caught the logic bugs. Cancelling an unbooked room still reported success, `90 * 1.15` gave `103.49999999999999`, negative surge multipliers were accepted, the ledger wasn't valid JSON, and `main()` threw away the booking log. I only found these by running the program and reading the output. A 10.00/10 Pylint score does not mean the code is correct.

### 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally:** a `pre-commit` hook that runs Flake8, Pylint and Bandit on staged files, so issues are fixed before they reach a commit. VS Code extensions for Pylint/Flake8 show the warnings while typing.
- **In CI:** a GitHub Actions workflow that runs all three tools on every push and pull request, and fails the build if Bandit finds any Medium/High issue, Flake8 reports anything, or the Pylint score drops below a threshold (e.g. `pylint --fail-under=9.5`).
- **Configuration:** keep shared settings (line length, disabled checks) in `pyproject.toml` / `.flake8` so the whole team uses the same rules, and suppress a finding with `# nosec` or `# pylint: disable=` only with a comment explaining why.
- **Alongside tests:** static analysis complements unit tests; it doesn't replace them. As question 2 shows, the logic bugs needed tests to catch them.

### 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Security:** no more shell injection (`os.system`), arbitrary code execution (`eval`), weak hashing (MD5 → SHA-256), predictable references (`random` → `secrets`) or leaked secrets. Bandit went from 6 issues (2 High) to none.
- **Robustness:** errors are no longer silently swallowed; functions return clear `True`/`False` results or raise meaningful exceptions. The ledger file is always closed (`with`) and has a fixed encoding. The mutable default bug is gone, so booking logs no longer leak between calls. The module can be imported without side effects (`if __name__ == "__main__"`).
- **Correctness:** cancellations are only reported when a booking actually existed; prices are valid 2-decimal amounts; the ledger is valid JSON.
- **Readability:** PEP 8 naming (`book_room`), docstrings on every function, f-strings, and a simpler `check_room_status`. Pylint improved from **5.32/10 to 10.00/10** and Flake8 from 7 issues to 0.
