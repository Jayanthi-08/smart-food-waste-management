"""Replays a scripted session (typed answers are echoed) to produce sample_output.txt."""
import builtins
from datetime import date
import food_waste_manager as fw

answers = iter([
    "1", "FD004", "Fresh Paneer", "Dairy", "-5", "abc", "8", "kg",
    "2026-09-30", "2026-09-25", "30-09-2026", "2026-10-02",        # add (with errors)
    "1", "FD001", "FD005", "Curd", "Dairy", "2", "kg", "2026-09-30", "2026-10-06",  # duplicate ID then ok
    "2", "6", "7", "3", "paneer", "3", "",                          # view, monitor, summary, search, empty search
    "4", "FD004", "reduce", "3",                                    # reduce stock
    "4", "FD004", "reduce", "50",                                   # reduce below zero
    "4", "XX99",                                    # unknown ID
    "5", "FD005", "5", "FD005",                                     # remove, remove again (not found)
    "9", "8",                                                       # bad menu choice, exit
])

def fake_input(prompt=""):
    value = next(answers)
    print(f"{prompt}{value}")
    return value

builtins.input = fake_input
fw.OPERATING_DATE = date(2026, 10, 1)   # same operating date as the assignment sample
fw.load_sample_data()
fw.main_menu()
