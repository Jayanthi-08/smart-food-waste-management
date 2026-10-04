"""Test-case evidence: run with   python test_food_waste.py -v"""
import unittest
from datetime import date

import food_waste_manager as fw

TODAY = date(2026, 10, 1)


class FoodWasteTests(unittest.TestCase):
    def setUp(self):
        fw.OPERATING_DATE = TODAY
        fw.inventory.clear()
        fw.create_item("FD001", "Milk", "Dairy", 12, "L", "2026-09-25", "2026-09-30")

    # 1. Valid food item
    def test_valid_item_added(self):
        rec = fw.create_item("FD002", "Rice", "Grain", "25", "kg",
                             "2026-09-01", "2027-02-15")
        self.assertEqual(rec["quantity"], 25)
        self.assertEqual(len(fw.inventory), 2)

    # 2. Duplicate item ID (also case-insensitive)
    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):
            fw.create_item("fd001", "Curd", "Dairy", 1, "kg", "2026-09-30", "2026-10-05")
        self.assertEqual(len(fw.inventory), 1)

    # 3 & 4. Negative / zero quantity
    def test_negative_quantity_rejected(self):
        with self.assertRaises(ValueError):
            fw.validate_quantity("-5")

    def test_zero_quantity_rejected(self):
        with self.assertRaises(ValueError):
            fw.validate_quantity("0")

    def test_non_numeric_and_empty_quantity_rejected(self):
        for bad in ("abc", "", "   ", "nan", "inf"):
            with self.assertRaises(ValueError, msg=bad):
                fw.validate_quantity(bad)

    # 5. Invalid date format
    def test_invalid_date_format_rejected(self):
        for bad in ("01-10-2026", "2026/10/01", "2026-13-01", "2026-02-30",
                    "2026-1-5", "tomorrow", ""):
            with self.assertRaises(ValueError, msg=bad):
                fw.validate_date(bad)

    # 6. Expiry before purchase
    def test_expiry_before_purchase_rejected(self):
        with self.assertRaises(ValueError):
            fw.create_item("FD009", "Bread", "Bakery", 2, "pcs",
                           "2026-09-30", "2026-09-25")

    # 7-9. Status classification + boundaries
    def test_expired(self):
        self.assertEqual(fw.calculate_status(date(2026, 9, 30), TODAY), "EXPIRED")

    def test_expiring_soon_boundaries(self):
        self.assertEqual(fw.calculate_status(date(2026, 10, 1), TODAY), "EXPIRING SOON")  # 0 days
        self.assertEqual(fw.calculate_status(date(2026, 10, 4), TODAY), "EXPIRING SOON")  # 3 days

    def test_available(self):
        self.assertEqual(fw.calculate_status(date(2026, 10, 5), TODAY), "AVAILABLE")      # 4 days

    # 10. Reduce stock below zero
    def test_reduce_below_zero_rejected(self):
        with self.assertRaises(ValueError):
            fw.change_quantity("FD001", "reduce", 13)
        self.assertEqual(fw.find_item("FD001")["quantity"], 12)

    def test_reduce_and_increase_work(self):
        self.assertEqual(fw.change_quantity("FD001", "reduce", 2)["quantity"], 10)
        self.assertEqual(fw.change_quantity("FD001", "increase", 5)["quantity"], 15)

    # 11. Unknown item ID
    def test_unknown_id(self):
        with self.assertRaises(ValueError):
            fw.change_quantity("NOPE", "reduce", 1)
        with self.assertRaises(ValueError):
            fw.delete_item("NOPE")

    # Extra: blank fields, search, delete, summary
    def test_blank_fields_rejected(self):
        with self.assertRaises(ValueError):
            fw.create_item("FD010", "  ", "Dairy", 1, "kg", "2026-09-30", "2026-10-05")
        with self.assertRaises(ValueError):
            fw.create_item("FD010", "Curd", "", 1, "kg", "2026-09-30", "2026-10-05")

    def test_search_by_name_and_category(self):
        self.assertEqual(len(fw.find_matches("milk")), 1)
        self.assertEqual(len(fw.find_matches("DAIRY")), 1)
        self.assertEqual(fw.find_matches("zzz"), [])

    def test_delete(self):
        fw.delete_item("fd001")
        self.assertEqual(fw.inventory, [])

    def test_summary(self):
        fw.create_item("FD002", "Tomatoes", "Veg", 15, "kg", "2026-09-28", "2026-10-02")
        fw.create_item("FD003", "Rice", "Grain", 25, "kg", "2026-09-01", "2027-02-15")
        s = fw.compute_summary(TODAY)
        self.assertEqual((s["records"], s["total_qty"]), (3, 52))
        self.assertEqual((s["expired"], s["soon"], s["available"], s["attention"]),
                         (1, 1, 1, 2))


if __name__ == "__main__":
    unittest.main()
