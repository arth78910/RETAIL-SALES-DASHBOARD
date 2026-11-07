"""CSV loading, validation, and export for retail sales records."""

import csv
import math
from datetime import date, datetime
from pathlib import Path


class SalesData:
    """Owns validated sales records and handles CSV file operations."""

    REQUIRED_COLUMNS = (
        "Order_ID",
        "Order_Date",
        "Product_Name",
        "Category",
        "Quantity",
        "Unit_Price",
        "Total_Amount",
        "Payment_Mode",
    )

    def __init__(self):
        self._records = []
        self.invalid_rows = 0

    @property
    def records(self):
        """Return a copy so callers cannot mutate the stored dataset."""
        return [record.copy() for record in self._records]

    def load_csv(self, file_path):
        """Load valid rows from a CSV, rejecting files with invalid headers."""
        path = Path(file_path)
        with path.open("r", newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            if not reader.fieldnames:
                raise ValueError("The CSV file is empty or has no header row.")

            headers = [header.strip() for header in reader.fieldnames]
            if len(headers) != len(set(headers)):
                raise ValueError("The CSV file contains duplicate column names.")

            missing = [column for column in self.REQUIRED_COLUMNS if column not in headers]
            if missing:
                raise ValueError(
                    "Missing required column(s): " + ", ".join(missing)
                )

            records = []
            invalid_rows = 0
            for raw_row in reader:
                row = {
                    (key.strip() if key else ""): value
                    for key, value in raw_row.items()
                }
                try:
                    records.append(self._validate_row(row))
                except (AttributeError, TypeError, ValueError):
                    invalid_rows += 1

        if not records:
            raise ValueError("No valid sales records were found in the CSV file.")

        self._records = records
        self.invalid_rows = invalid_rows
        return len(records)

    @staticmethod
    def _parse_date(value):
        value = value.strip()
        try:
            return date.fromisoformat(value)
        except ValueError:
            for date_format in ("%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    return datetime.strptime(value, date_format).date()
                except ValueError:
                    continue
        raise ValueError("Order_Date must be a valid date.")

    @classmethod
    def _validate_row(cls, row):
        text_fields = ("Order_ID", "Product_Name", "Category", "Payment_Mode")
        clean = {field: (row.get(field) or "").strip() for field in text_fields}
        if any(not value for value in clean.values()):
            raise ValueError("A required text value is missing.")

        quantity = int((row.get("Quantity") or "").strip())
        unit_price = float((row.get("Unit_Price") or "").strip())
        total_amount = float((row.get("Total_Amount") or "").strip())
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if (
            not math.isfinite(unit_price)
            or not math.isfinite(total_amount)
            or unit_price < 0
            or total_amount < 0
        ):
            raise ValueError("Prices must be finite, non-negative numbers.")

        clean.update(
            {
                "Order_Date": cls._parse_date(row.get("Order_Date") or ""),
                "Quantity": quantity,
                "Unit_Price": unit_price,
                "Total_Amount": total_amount,
            }
        )
        return clean

    @classmethod
    def export_csv(cls, file_path, records):
        """Write validated records using the documented CSV column order."""
        path = Path(file_path)
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=cls.REQUIRED_COLUMNS)
            writer.writeheader()
            for record in records:
                exported = record.copy()
                order_date = exported.get("Order_Date")
                if isinstance(order_date, date):
                    exported["Order_Date"] = order_date.isoformat()
                writer.writerow(exported)
