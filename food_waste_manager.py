"""
Smart Food-Waste Management System
==================================
A menu-driven inventory tracker that classifies food items as
EXPIRED, EXPIRING SOON or AVAILABLE so staff can act before food is wasted.

Design idea: every business operation is split into two layers
  1. LOGIC functions  (validate_*, calculate_status, change_quantity, ...)
     -> no input()/print(); they return a value or raise ValueError.
        This makes them easy to test.
  2. UI functions     (add_item, update_quantity, ...)
     -> talk to the user, call the logic functions, catch errors and
        show a friendly message instead of crashing.
"""

import math
from datetime import date, datetime, timedelta

# --------------------------------------------------------------------------
# Constants (thresholds and status labels live in ONE place)
# --------------------------------------------------------------------------
EXPIRING_SOON_DAYS = 3          # 0-3 days remaining => EXPIRING SOON
DATE_FORMAT = "%Y-%m-%d"
STATUS_EXPIRED = "EXPIRED"
STATUS_SOON = "EXPIRING SOON"
STATUS_AVAILABLE = "AVAILABLE"
EXPIRED_KEY, SOON_KEY, AVAILABLE_KEY = "expired", "soon", "available"  # summary dict keys

# --------------------------------------------------------------------------
# Global state: the inventory is a LIST of DICTIONARIES (one dict per item)
# --------------------------------------------------------------------------
inventory = []
OPERATING_DATE = date.today()   # the "current operating date"


def log(tag, message):
    """Print a message in the [TAG] style used by the sample output."""
    print(f"[{tag}] {message}")


# ==========================================================================
# VALIDATION (logic layer) - each function raises ValueError on bad input
# ==========================================================================
def validate_date(text):
    """Convert 'YYYY-MM-DD' text into a date object, or raise ValueError."""
    text = str(text).strip()
    if not text:
        raise ValueError("Date cannot be empty.")
    try:
        parsed = datetime.strptime(text, DATE_FORMAT).date()
    except ValueError:
        raise ValueError("Invalid date. Use YYYY-MM-DD and a real calendar date "
                         "(e.g. 2026-10-01).")
    # strptime accepts '2026-1-5'; insist on the exact YYYY-MM-DD shape.
    if parsed.isoformat() != text:
        raise ValueError("Date must follow YYYY-MM-DD exactly (e.g. 2026-10-01).")
    return parsed


def validate_quantity(text):
    """Return a positive number (int if whole, else float), or raise ValueError."""
    text = str(text).strip()
    if not text:
        raise ValueError("Quantity cannot be empty.")
    try:
        number = float(text)
    except ValueError:
        raise ValueError("Quantity must be a number.")
    if not math.isfinite(number):          # blocks 'nan' and 'inf'
        raise ValueError("Quantity must be a real number.")
    if number <= 0:
        raise ValueError("Quantity must be greater than zero. Please try again.")
    return int(number) if number.is_integer() else number


def validate_non_empty(text, field_name):
    """Return the stripped text, or raise ValueError if it is blank."""
    text = str(text).strip()
    if not text:
        raise ValueError(f"{field_name} cannot be blank.")
    return text


def find_item(item_id):
    """Return the dict whose id matches item_id (case-insensitive), else None."""
    wanted = str(item_id).strip().upper()
    for item in inventory:
        if item["id"].upper() == wanted:
            return item
    return None


def validate_new_id(text):
    """ID must be non-blank and not already used."""
    item_id = validate_non_empty(text, "Item ID").upper()
    if find_item(item_id) is not None:
        raise ValueError(f"Item ID {item_id} already exists. IDs must be unique.")
    return item_id


def validate_expiry(text, purchase_date):
    """Expiry must be a valid date and not earlier than the purchase date."""
    expiry = validate_date(text)
    if expiry < purchase_date:
        raise ValueError("Expiry date cannot be earlier than purchase date.")
    return expiry


# ==========================================================================
# CORE BUSINESS LOGIC
# ==========================================================================
def calculate_status(expiry_date, today=None):
    """Classify an expiry date relative to the operating date."""
    today = today or OPERATING_DATE
    days_left = (expiry_date - today).days
    if days_left < 0:
        return STATUS_EXPIRED
    elif days_left <= EXPIRING_SOON_DAYS:
        return STATUS_SOON
    else:
        return STATUS_AVAILABLE


def item_status(item, today=None):
    """Status of a stored item (its expiry is stored as a YYYY-MM-DD string)."""
    return calculate_status(validate_date(item["expiry_date"]), today)


def create_item(item_id, name, category, quantity, unit, purchase_date, expiry_date):
    """Validate every field, build the dictionary and append it to inventory."""
    purchase = validate_date(purchase_date)
    record = {
        "id": validate_new_id(item_id),
        "name": validate_non_empty(name, "Food name"),
        "category": validate_non_empty(category, "Category"),
        "quantity": validate_quantity(quantity),
        "unit": validate_non_empty(unit, "Unit"),
        "purchase_date": purchase.isoformat(),
        "expiry_date": validate_expiry(expiry_date, purchase).isoformat(),
    }
    inventory.append(record)
    return record


def find_matches(term):
    """Case-insensitive partial match on item name OR category."""
    term = validate_non_empty(term, "Search text").lower()
    return [item for item in inventory
            if term in item["name"].lower() or term in item["category"].lower()]


def change_quantity(item_id, operation, amount):
    """Increase/reduce stock. Returns the new quantity or raises ValueError."""
    item = find_item(item_id)
    if item is None:
        raise ValueError(f"Item ID '{str(item_id).strip()}' not found.")
    amount = validate_quantity(amount)
    operation = str(operation).strip().lower()
    if operation in ("increase", "add", "i", "+"):
        item["quantity"] += amount
    elif operation in ("reduce", "decrease", "r", "-"):
        if amount > item["quantity"]:
            raise ValueError(f"Cannot reduce by {amount}: only "
                             f"{item['quantity']} {item['unit']} in stock.")
        item["quantity"] -= amount
    else:
        raise ValueError("Operation must be 'increase' or 'reduce'.")
    return item


def delete_item(item_id):
    """Remove a record by unique ID; raise ValueError if it does not exist."""
    item = find_item(item_id)
    if item is None:
        raise ValueError(f"Item ID '{str(item_id).strip()}' not found.")
    inventory.remove(item)
    return item


def compute_summary(today=None):
    """Return a dictionary of operational metrics."""
    summary = {"records": len(inventory), "total_qty": 0,
               EXPIRED_KEY: 0, SOON_KEY: 0, AVAILABLE_KEY: 0,
               "expired_qty": 0, "attention_qty": 0}
    for item in inventory:
        status = item_status(item, today)
        summary["total_qty"] += item["quantity"]
        if status == STATUS_EXPIRED:
            summary[EXPIRED_KEY] += 1
            summary["expired_qty"] += item["quantity"]
        elif status == STATUS_SOON:
            summary[SOON_KEY] += 1
        else:
            summary[AVAILABLE_KEY] += 1
        if status != STATUS_AVAILABLE:
            summary["attention_qty"] += item["quantity"]
    summary["attention"] = summary[EXPIRED_KEY] + summary[SOON_KEY]
    return summary



# ==========================================================================
# INPUT HELPER - keeps asking until the validator accepts the answer
# ==========================================================================
def ask(prompt, validator):
    """Loop (while) until validator(text) succeeds; print errors, never crash."""
    while True:
        text = input(prompt)
        try:
            return validator(text)
        except ValueError as error:
            log("ERROR", error)


# ==========================================================================
# UI FUNCTIONS (what the menu calls)
# ==========================================================================
def add_item():
    print("\n--- ADD FOOD ITEM ---")
    item_id = ask("Item ID : ", validate_new_id)
    name = ask("Food Name : ", lambda t: validate_non_empty(t, "Food name"))
    category = ask("Category : ", lambda t: validate_non_empty(t, "Category"))
    quantity = ask("Quantity : ", validate_quantity)
    unit = ask("Unit : ", lambda t: validate_non_empty(t, "Unit"))
    purchase = ask("Purchase Date (YYYY-MM-DD) : ", validate_date)
    expiry = ask("Expiry Date (YYYY-MM-DD) : ",
                 lambda t: validate_expiry(t, purchase))
    try:
        create_item(item_id, name, category, quantity, unit,
                    purchase.isoformat(), expiry.isoformat())
        log("SUCCESS", f"Food item {item_id} added successfully.")
    except ValueError as error:          # safety net for any rule we missed
        log("ERROR", error)


def view_inventory():
    print("\n--- CURRENT INVENTORY ---")
    if not inventory:
        log("INFO", "Inventory is empty.")
        return
    print(f"{'ID':<8}{'ITEM':<18}{'CATEGORY':<12}{'QTY':<14}"
          f"{'PURCHASED':<12}{'EXPIRY':<12}STATUS")
    print("-" * 88)
    for item in inventory:
        qty = f"{item['quantity']} {item['unit']}"
        print(f"{item['id']:<8}{item['name']:<18}{item['category']:<12}{qty:<14}"
              f"{item['purchase_date']:<12}{item['expiry_date']:<12}"
              f"{item_status(item)}")


def search_item():
    term = input("Search item: ")
    try:
        matches = find_matches(term)
    except ValueError as error:
        log("ERROR", error)
        return
    if not matches:
        log("INFO", f"No items match '{term.strip()}'.")
        return
    for item in matches:
        log("RESULT", f"{item['id']} | {item['name']} | {item['category']} | "
                      f"{item['quantity']} {item['unit']} | {item_status(item)}")


def update_quantity():
    item_id = input("Item ID: ")
    if find_item(item_id) is None:
        log("ERROR", f"Item ID '{item_id.strip()}' not found.")
        return
    operation = input("Operation (increase/reduce): ")
    amount = input("Quantity: ")
    try:
        item = change_quantity(item_id, operation, amount)
        log("SUCCESS", "Quantity updated.")
        log("INFO", f"Remaining stock: {item['quantity']} {item['unit']}")
    except ValueError as error:
        log("ERROR", error)


def remove_item():
    item_id = input("Item ID to remove: ")
    try:
        item = delete_item(item_id)
        log("SUCCESS", f"Removed {item['id']} ({item['name']}).")
    except ValueError as error:
        log("ERROR", error)


def expiry_monitor():
    print("\n--- EXPIRY MONITOR ---")
    if not inventory:
        log("INFO", "Inventory is empty.")
        return
    print(f"{'ID':<8}{'ITEM':<18}{'QTY':<12}{'EXPIRY':<12}{'STATUS':<15}ACTION")
    expired = soon = 0
    for item in sorted(inventory, key=lambda i: i["expiry_date"]):
        status = item_status(item)
        if status == STATUS_EXPIRED:
            expired += 1
            action = "DISPOSE (food-safety rules)"
        elif status == STATUS_SOON:
            soon += 1
            action = "USE / DONATE NOW"
        else:
            action = "-"
        qty = f"{item['quantity']} {item['unit']}"
        print(f"{item['id']:<8}{item['name']:<18}{qty:<12}"
              f"{item['expiry_date']:<12}{status:<15}{action}")
    if expired:
        log("ALERT", f"{expired} item{'s have' if expired > 1 else ' has'} expired.")
    if soon:
        log("ALERT", f"{soon} item{'s' if soon > 1 else ''} require attention "
                     f"within {EXPIRING_SOON_DAYS} days.")
    if not expired and not soon:
        log("INFO", "No items need attention.")


def generate_summary():
    s = compute_summary()
    print("\n--- INVENTORY SUMMARY ---")
    print(f"Total food records       : {s['records']}")
    print(f"Total quantity           : {s['total_qty']}  (units are mixed)")
    print(f"Expired items            : {s[EXPIRED_KEY]}")
    print(f"Expiring-soon items      : {s[SOON_KEY]}")
    print(f"Available items          : {s[AVAILABLE_KEY]}")
    print(f"Attention-required items : {s['attention']}")
    print(f"Expired stock quantity   : {s['expired_qty']}")
    print(f"Attention-required qty   : {s['attention_qty']}")
    if s["attention"]:
        log("RECOMMENDATION",
            "Prioritize expired stock for disposal according to organizational "
            "food-safety procedures and review expiring-soon stock for immediate "
            "consumption, redistribution, or donation where appropriate.")
    else:
        log("INFO", "All stock is currently within safe dates.")


# ==========================================================================
# SAMPLE DATA + MENU
# ==========================================================================
def load_sample_data(today=None):
    """Start with a few records; dates are relative so the demo never goes stale."""
    today = today or OPERATING_DATE
    d = lambda offset: (today + timedelta(days=offset)).isoformat()
    inventory.clear()
    create_item("FD001", "Milk", "Dairy", 12, "L", d(-5), d(-1))
    create_item("FD002", "Tomatoes", "Vegetable", 15, "kg", d(-4), d(1))
    create_item("FD003", "Rice", "Grain", 25, "kg", d(-30), d(137))


MENU = """
==================================================
        SMART FOOD-WASTE MANAGEMENT SYSTEM
==================================================
1. Add Food Item
2. View Inventory
3. Search Food Item
4. Update Quantity
5. Remove Food Item
6. Expiry Monitoring
7. Inventory Summary
8. Exit
--------------------------------------------------"""


def main_menu():
    log("INFO", "Smart Food-Waste Management System started")
    log("INFO", f"Operating date: {OPERATING_DATE.isoformat()}")
    while True:
        print(MENU)
        try:
            choice = input("Enter your choice: ").strip()
        except (EOFError, KeyboardInterrupt):     # Ctrl+D / Ctrl+C / no more input
            print()
            choice = "8"
        if choice == "1":
            add_item()
        elif choice == "2":
            view_inventory()
        elif choice == "3":
            search_item()
        elif choice == "4":
            update_quantity()
        elif choice == "5":
            remove_item()
        elif choice == "6":
            expiry_monitor()
        elif choice == "7":
            generate_summary()
        elif choice == "8":
            log("INFO", "Application closed successfully.")
            break
        else:
            log("ERROR", "Invalid choice. Please enter a number from 1 to 8.")


if __name__ == "__main__":
    OPERATING_DATE = date.today()
    load_sample_data()
    main_menu()
