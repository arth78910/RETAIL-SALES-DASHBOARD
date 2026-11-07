"""Filtering, KPI calculations, and business insights."""

from collections import defaultdict
from datetime import datetime


class SalesAnalyzer:
    """Analyze sales records without changing the source dataset."""

    def filter_records(
        self,
        records,
        start_date=None,
        end_date=None,
        category="All Categories",
        product_query="",
    ):
        if start_date and end_date and start_date > end_date:
            raise ValueError("Start date must be on or before end date.")

        query = product_query.strip().casefold()
        filtered = []
        for record in records:
            order_date = record["Order_Date"]
            if start_date and order_date < start_date:
                continue
            if end_date and order_date > end_date:
                continue
            if category != "All Categories" and record["Category"] != category:
                continue
            if query and query not in record["Product_Name"].casefold():
                continue
            filtered.append(record)
        return filtered

    @staticmethod
    def calculate_kpis(records):
        revenue = sum(record["Total_Amount"] for record in records)
        order_count = len({record["Order_ID"] for record in records})
        units_sold = sum(record["Quantity"] for record in records)
        return {
            "revenue": revenue,
            "orders": order_count,
            "units_sold": units_sold,
            "average_order_value": revenue / order_count if order_count else 0,
        }

    @staticmethod
    def category_revenue(records):
        totals = defaultdict(float)
        for record in records:
            totals[record["Category"]] += record["Total_Amount"]
        return dict(sorted(totals.items()))

    @staticmethod
    def monthly_revenue(records):
        totals = defaultdict(float)
        for record in records:
            month = record["Order_Date"].strftime("%Y-%m")
            totals[month] += record["Total_Amount"]
        return dict(sorted(totals.items()))

    @staticmethod
    def daily_revenue(records):
        totals = defaultdict(float)
        for record in records:
            totals[record["Order_Date"]] += record["Total_Amount"]
        return dict(sorted(totals.items()))

    @staticmethod
    def top_products(records, limit=5):
        totals = defaultdict(int)
        for record in records:
            totals[record["Product_Name"]] += record["Quantity"]
        ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
        return ranked[:limit]

    def business_insights(self, records):
        if not records:
            return [
                "No sales records match the selected filters.",
                "Adjust the date range, category, or product search to continue.",
            ]

        revenue_by_category = self.category_revenue(records)
        revenue_by_month = self.monthly_revenue(records)
        revenue_by_product = defaultdict(float)
        for record in records:
            revenue_by_product[record["Product_Name"]] += record["Total_Amount"]

        best_product = max(revenue_by_product.items(), key=lambda item: item[1])
        best_category = max(revenue_by_category.items(), key=lambda item: item[1])
        best_month = max(revenue_by_month.items(), key=lambda item: item[1])
        kpis = self.calculate_kpis(records)
        return [
            "Best-performing product: {} ({})".format(
                best_product[0], self._currency(best_product[1])
            ),
            "Highest-revenue category: {} ({})".format(
                best_category[0], self._currency(best_category[1])
            ),
            "Highest-sales month: {} ({})".format(
                datetime.strptime(best_month[0], "%Y-%m").strftime("%B %Y"),
                self._currency(best_month[1]),
            ),
            "Total revenue across filtered records: {}".format(
                self._currency(kpis["revenue"])
            ),
        ]

    @staticmethod
    def _currency(amount):
        return "Rs. {:,.2f}".format(amount)
