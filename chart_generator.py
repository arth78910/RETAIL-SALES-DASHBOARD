"""Matplotlib chart creation for the retail dashboard."""

import matplotlib.dates as mdates
from matplotlib.figure import Figure


class ChartGenerator:
    """Build styled Matplotlib figures from already-filtered sales records."""

    NAVY = "#172554"
    BLUE = "#2563EB"
    TEAL = "#0F9D8A"
    ORANGE = "#F59E0B"
    PURPLE = "#8B5CF6"
    PALETTE = (BLUE, TEAL, ORANGE, PURPLE, "#E85D75", "#38A3A5")

    def __init__(self):
        self.figure_size = (5.5, 3.15)

    def _figure(self, title, ylabel=None):
        figure = Figure(figsize=self.figure_size, dpi=100, facecolor="white")
        axes = figure.add_subplot(111)
        axes.set_title(title, loc="left", fontsize=11, fontweight="bold", color=self.NAVY)
        if ylabel:
            axes.set_ylabel(ylabel, fontsize=8, color="#64748B")
        axes.tick_params(axis="both", labelsize=8, colors="#64748B")
        axes.spines["top"].set_visible(False)
        axes.spines["right"].set_visible(False)
        axes.spines["left"].set_color("#E2E8F0")
        axes.spines["bottom"].set_color("#E2E8F0")
        axes.grid(axis="y", color="#E2E8F0", linewidth=0.7, alpha=0.8)
        figure.tight_layout(pad=2)
        return figure, axes

    @staticmethod
    def _empty(axes):
        axes.text(
            0.5,
            0.5,
            "No data for the selected filters",
            ha="center",
            va="center",
            transform=axes.transAxes,
            color="#64748B",
            fontsize=9,
        )
        axes.set_axis_off()

    def monthly_revenue_chart(self, records, analyzer):
        figure, axes = self._figure("Monthly Revenue", "Revenue (Rs.)")
        totals = analyzer.monthly_revenue(records)
        if not totals:
            self._empty(axes)
        else:
            labels, values = zip(*totals.items())
            axes.plot(labels, values, color=self.BLUE, linewidth=2.2, marker="o", markersize=4)
            axes.fill_between(labels, values, color=self.BLUE, alpha=0.1)
            axes.set_xlabel("Month", fontsize=8, color="#64748B")
            axes.tick_params(axis="x", rotation=35)
        figure.tight_layout(pad=2)
        return figure

    def category_sales_chart(self, records, analyzer):
        figure, axes = self._figure("Revenue by Category", "Revenue (Rs.)")
        totals = analyzer.category_revenue(records)
        if not totals:
            self._empty(axes)
        else:
            labels, values = zip(*totals.items())
            colors = [self.PALETTE[index % len(self.PALETTE)] for index in range(len(labels))]
            bars = axes.bar(labels, values, color=colors, width=0.62)
            axes.set_xlabel("Category", fontsize=8, color="#64748B")
            axes.tick_params(axis="x", rotation=20)
            axes.bar_label(bars, fmt="%.0f", fontsize=7, padding=2, color="#475569")
        figure.tight_layout(pad=2)
        return figure

    def category_distribution_chart(self, records, analyzer):
        figure, axes = self._figure("Sales Distribution by Category")
        totals = analyzer.category_revenue(records)
        if not totals or sum(totals.values()) == 0:
            self._empty(axes)
        else:
            axes.grid(False)
            colors = [self.PALETTE[index % len(self.PALETTE)] for index in range(len(totals))]
            axes.pie(
                list(totals.values()),
                labels=list(totals.keys()),
                autopct="%1.1f%%",
                startangle=90,
                colors=colors,
                textprops={"fontsize": 8, "color": self.NAVY},
                wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
            )
            axes.axis("equal")
        figure.tight_layout(pad=1)
        return figure

    def top_products_chart(self, records, analyzer):
        figure, axes = self._figure("Top 5 Best-Selling Products", "Units sold")
        products = analyzer.top_products(records)
        if not products:
            self._empty(axes)
        else:
            labels, values = zip(*products)
            positions = range(len(labels))
            bars = axes.barh(positions, values, color=self.TEAL, height=0.58)
            axes.set_yticks(list(positions), labels)
            axes.invert_yaxis()
            axes.set_xlabel("Quantity sold", fontsize=8, color="#64748B")
            axes.bar_label(bars, padding=3, fontsize=8, color="#475569")
        figure.tight_layout(pad=2)
        return figure

    def daily_sales_chart(self, records, analyzer):
        figure, axes = self._figure("Daily Sales Trend", "Revenue (Rs.)")
        totals = analyzer.daily_revenue(records)
        if not totals:
            self._empty(axes)
        else:
            dates, values = zip(*totals.items())
            axes.plot(dates, values, color=self.PURPLE, linewidth=1.8, marker=".", markersize=4)
            axes.set_xlabel("Date", fontsize=8, color="#64748B")
            axes.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=8))
            axes.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
            figure.autofmt_xdate(rotation=25)
        figure.tight_layout(pad=2)
        return figure
