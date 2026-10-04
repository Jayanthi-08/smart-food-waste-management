# Smart Food-Waste Management System

A menu-driven Python application that tracks food inventory and classifies each item as
**EXPIRED**, **EXPIRING SOON** (0–3 days left) or **AVAILABLE** (more than 3 days left), so
staff can use, donate or dispose of stock before it is wasted.

## Files

| File | Purpose |
|---|---|
| `food_waste_manager.py` | The application (run this) |
| `test_food_waste.py` | Automated test cases (17 tests, all pass) |
| `test_results.txt` | Saved output of the test run (test-case evidence) |
| `run_demo.py` | Replays a scripted session to generate the sample output |
| `sample_output.txt` | Sample session transcript |

## How to run

```
python food_waste_manager.py        # start the application
python test_food_waste.py -v        # run the tests
```
Requires Python 3.8+ and only the standard library (`datetime`, `math`).

## Application workflow

1. On start-up the operating date is set to today and three sample records are loaded.
2. `main_menu()` shows the menu inside a `while True` loop and calls the matching function.
3. Every function that accepts user input validates it; an invalid value produces an
   `[ERROR]` message and the user is asked again — the program never crashes on bad input.
4. Choosing **8** (or pressing Ctrl+C / Ctrl+D) exits cleanly.

| Menu | Function | What it does |
|---|---|---|
| 1 | `add_item()` | Prompts for each field, validating as it goes |
| 2 | `view_inventory()` | Formatted table with live status |
| 3 | `search_item()` | Case-insensitive partial match on name or category |
| 4 | `update_quantity()` | Increase/reduce stock; blocks negative stock |
| 5 | `remove_item()` | Delete by unique ID |
| 6 | `expiry_monitor()` | Sorted by expiry date, with alerts and suggested action |
| 7 | `generate_summary()` | Counts, quantities, attention-required stock, recommendation |
| 8 | – | Exit |

## Python concepts used

- **Variables / constants** – `EXPIRING_SOON_DAYS`, status labels, `OPERATING_DATE`.
- **Data types** – `str` (names, dates), `int`/`float` (quantity), `bool` (checks), `date` objects.
- **Lists** – `inventory` holds every record.
- **Dictionaries** – each item is `{"id", "name", "category", "quantity", "unit", "purchase_date", "expiry_date"}`.
- **Functions** – one function per business operation, split into logic and UI layers.
- **Control structures** – `if/elif/else` for status classification and menu dispatch; `for` to scan the
  list; `while` for the menu and for re-prompting.
- **Exception handling** – validators `raise ValueError`; callers use `try/except ValueError`;
  `EOFError`/`KeyboardInterrupt` are caught in the menu.
- **String formatting** – f-strings with alignment (`{name:<18}`) for tables and messages.
- **Modules** – `datetime` (parsing, date arithmetic, `timedelta`), `math` (`isfinite`).

## Business rules implemented

Unique IDs (case-insensitive) · name/category/unit not blank · quantity positive numeric ·
dates strictly `YYYY-MM-DD` and real calendar dates · expiry not before purchase · stock can
never go negative · expired = expiry date before operating date · 0–3 days left = expiring soon.

## Notes / assumptions

- Data is held in memory only (it resets when the program closes). CSV/JSON persistence would be
  the natural next enhancement.
- "Total quantity" adds quantities across different units (as in the assignment's sample), so it is
  a record-level count rather than a physical measure.
- A quantity may be reduced to exactly zero (not negative); the record stays until removed.
