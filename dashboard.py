"""Tkinter user interface for the Retail Sales Analytics Dashboard."""

from datetime import date
from pathlib import Path
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from chart_generator import ChartGenerator
from sales_analyzer import SalesAnalyzer
from sales_data import SalesData


class DashboardApp:
    """Coordinate dashboard views, filters, CSV uploads, and report exports."""

    BACKGROUND = "#F3F6FB"
    NAVY = "#14213D"
    MUTED = "#64748B"
    ACCENT = "#2563EB"
    CURRENCY = "Rs."

    def __init__(self, root):
        self.root = root
        self.root.title("Retail Sales Analytics Dashboard")
        self.root.geometry("1440x920")
        self.root.minsize(1120, 760)
        self.root.configure(bg=self.BACKGROUND)

        self.data = SalesData()
        self.analyzer = SalesAnalyzer()
        self.chart_generator = ChartGenerator()
        self.filtered_records = []
        self.active_page = "Overview"

        self._configure_styles()
        self._build_shell()
        sample_path = Path(__file__).resolve().parent / "data" / "retail_sales.csv"
        try:
            self.data.load_csv(sample_path)
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror("Sample data error", str(error), parent=self.root)
        self._show_overview()
        self._refresh_status()

    def _configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground=self.NAVY,
            rowheight=32,
            borderwidth=0,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background="#EEF2F8",
            foreground=self.NAVY,
            font=("Segoe UI", 9, "bold"),
            padding=(8, 9),
        )
        style.map("Treeview", background=[("selected", "#DBEAFE")])
        style.configure("TCombobox", padding=7, fieldbackground="white")

    def _build_shell(self):
        self.sidebar = tk.Frame(self.root, bg=self.NAVY, width=228)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="NORTHSTAR",
            bg=self.NAVY,
            fg="white",
            font=("Segoe UI", 17, "bold"),
        ).pack(anchor="w", padx=24, pady=(28, 2))
        tk.Label(
            self.sidebar,
            text="RETAIL INTELLIGENCE",
            bg=self.NAVY,
            fg="#9FB2D0",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=25, pady=(0, 36))

        self.nav_buttons = {}
        self._add_nav_button("Overview", self._show_overview)
        self._add_nav_button("Sales records", self._show_records)

        tk.Frame(self.sidebar, bg="#34425C", height=1).pack(fill="x", padx=20, pady=22)
        tk.Label(
            self.sidebar,
            text="DATA",
            bg=self.NAVY,
            fg="#8295B5",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=24, pady=(0, 8))
        self._add_nav_button("Upload CSV", self._upload_csv)
        self._add_nav_button("Export filtered CSV", self._export_csv)

        tk.Label(
            self.sidebar,
            text="CSV-powered insights\nBuilt for better decisions",
            bg=self.NAVY,
            fg="#9FB2D0",
            font=("Segoe UI", 9),
            justify="left",
        ).pack(side="bottom", anchor="w", padx=24, pady=24)

        self.main_area = tk.Frame(self.root, bg=self.BACKGROUND)
        self.main_area.pack(side="left", fill="both", expand=True)
        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(
            self.main_area,
            textvariable=self.status_var,
            bg=self.BACKGROUND,
            fg=self.MUTED,
            font=("Segoe UI", 8),
            anchor="w",
        )
        status.pack(side="bottom", fill="x", padx=30, pady=(0, 12))
        self.page_container = tk.Frame(self.main_area, bg=self.BACKGROUND)
        self.page_container.pack(side="top", fill="both", expand=True)

    def _add_nav_button(self, label, command):
        button = tk.Button(
            self.sidebar,
            text="   " + label,
            command=command,
            anchor="w",
            relief="flat",
            bd=0,
            padx=14,
            pady=11,
            bg=self.NAVY,
            fg="#DCE5F4",
            activebackground="#22375E",
            activeforeground="white",
            font=("Segoe UI", 10),
            cursor="hand2",
        )
        button.pack(fill="x", padx=12, pady=2)
        self.nav_buttons[label] = button

    def _set_active_nav(self, label):
        self.active_page = label
        for name, button in self.nav_buttons.items():
            button.configure(bg="#22375E" if name == label else self.NAVY)

    def _clear_page(self):
        for widget in self.page_container.winfo_children():
            widget.destroy()

    def _page_header(self, title, subtitle):
        header = tk.Frame(self.page_container, bg=self.BACKGROUND)
        header.pack(fill="x", padx=32, pady=(25, 16))
        tk.Label(
            header,
            text=title,
            bg=self.BACKGROUND,
            fg=self.NAVY,
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text=subtitle,
            bg=self.BACKGROUND,
            fg=self.MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(3, 0))

    def _show_overview(self):
        self._set_active_nav("Overview")
        self._clear_page()
        self._page_header(
            "Retail sales overview",
            "Monitor revenue, orders, and product performance from your sales data.",
        )
        self._build_filters()

        self.overview_scroll = tk.Canvas(
            self.page_container, bg=self.BACKGROUND, highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            self.page_container, orient="vertical", command=self.overview_scroll.yview
        )
        self.overview_scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 8))
        self.overview_scroll.pack(side="left", fill="both", expand=True)
        self.overview_content = tk.Frame(self.overview_scroll, bg=self.BACKGROUND)
        self.content_window = self.overview_scroll.create_window(
            (0, 0), window=self.overview_content, anchor="nw"
        )
        self.overview_content.bind("<Configure>", self._update_scroll_region)
        self.overview_scroll.bind("<Configure>", self._resize_overview_content)
        self._build_kpis()
        self._build_insights()
        self._build_charts()
        self._refresh_overview()

    def _update_scroll_region(self, _event):
        self.overview_scroll.configure(
            scrollregion=self.overview_scroll.bbox("all")
        )

    def _resize_overview_content(self, event):
        self.overview_scroll.itemconfigure(self.content_window, width=event.width)

    def _build_filters(self):
        panel = tk.Frame(self.page_container, bg="white", padx=16, pady=13)
        panel.pack(fill="x", padx=32, pady=(0, 14))
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        self.category_var = tk.StringVar(value="All Categories")
        self.product_var = tk.StringVar()

        fields = [
            ("From date", self.start_var, 13),
            ("To date", self.end_var, 13),
        ]
        for label, variable, width in fields:
            field = tk.Frame(panel, bg="white")
            field.pack(side="left", padx=(0, 12))
            tk.Label(
                field, text=label, bg="white", fg=self.MUTED, font=("Segoe UI", 8, "bold")
            ).pack(anchor="w", pady=(0, 4))
            tk.Entry(
                field,
                textvariable=variable,
                width=width,
                relief="solid",
                bd=1,
                highlightthickness=0,
                font=("Segoe UI", 9),
            ).pack(ipady=6)

        category_field = tk.Frame(panel, bg="white")
        category_field.pack(side="left", padx=(0, 12))
        tk.Label(
            category_field,
            text="Category",
            bg="white",
            fg=self.MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        self.category_combo = ttk.Combobox(
            category_field,
            textvariable=self.category_var,
            state="readonly",
            width=20,
            values=["All Categories"],
        )
        self.category_combo.pack(ipady=3)

        product_field = tk.Frame(panel, bg="white")
        product_field.pack(side="left", padx=(0, 12))
        tk.Label(
            product_field,
            text="Product",
            bg="white",
            fg=self.MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        tk.Entry(
            product_field,
            textvariable=self.product_var,
            width=22,
            relief="solid",
            bd=1,
            font=("Segoe UI", 9),
        ).pack(ipady=6)

        tk.Button(
            panel,
            text="Apply filters",
            command=self._apply_filters,
            bg=self.ACCENT,
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="flat",
            padx=15,
            pady=9,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="left", padx=(4, 8), pady=(14, 0))
        tk.Button(
            panel,
            text="Reset",
            command=self._reset_filters,
            bg="#EEF2F8",
            fg=self.NAVY,
            activebackground="#E2E8F0",
            relief="flat",
            padx=13,
            pady=9,
            font=("Segoe UI", 9),
            cursor="hand2",
        ).pack(side="left", pady=(14, 0))
        self._update_category_options()

    def _update_category_options(self):
        if self.active_page != "Overview":
            return
        categories = sorted({row["Category"] for row in self.data.records})
        options = ["All Categories"] + categories
        self.category_combo.configure(values=options)
        if self.category_var.get() not in options:
            self.category_var.set("All Categories")

    def _build_kpis(self):
        self.kpi_frame = tk.Frame(self.overview_content, bg=self.BACKGROUND)
        self.kpi_frame.pack(fill="x", padx=32, pady=(0, 15))
        for column in range(4):
            self.kpi_frame.grid_columnconfigure(column, weight=1, uniform="kpi")
        self.kpi_values = {}
        cards = [
            ("Total revenue", "revenue", self.ACCENT),
            ("Total orders", "orders", "#0F9D8A"),
            ("Products sold", "units_sold", "#F59E0B"),
            ("Average order value", "average_order_value", "#8B5CF6"),
        ]
        for column, (title, key, color) in enumerate(cards):
            self.kpi_values[key] = self._create_kpi_card(
                self.kpi_frame, column, title, color
            )

    def _create_kpi_card(self, parent, column, title, accent):
        canvas = tk.Canvas(
            parent,
            height=112,
            bg=self.BACKGROUND,
            highlightthickness=0,
            bd=0,
        )
        canvas.grid(row=0, column=column, sticky="ew", padx=(0, 12))
        title_label = tk.Label(
            canvas, text=title.upper(), bg="white", fg=self.MUTED, font=("Segoe UI", 8, "bold")
        )
        value_label = tk.Label(
            canvas, text="--", bg="white", fg=self.NAVY, font=("Segoe UI", 19, "bold")
        )
        canvas.create_window(18, 19, window=title_label, anchor="nw")
        canvas.create_window(18, 49, window=value_label, anchor="nw")

        def draw_card(event):
            canvas.delete("card")
            points = self._rounded_rectangle_points(event.width, 108, 14)
            canvas.create_polygon(
                points,
                smooth=True,
                fill="white",
                outline="#E7ECF3",
                tags="card",
            )
            canvas.create_line(
                14, 17, 14, 91, fill=accent, width=4, capstyle="round", tags="card"
            )
            canvas.tag_lower("card")

        canvas.bind("<Configure>", draw_card)
        return value_label

    @staticmethod
    def _rounded_rectangle_points(width, height, radius):
        return [
            radius, 0, width - radius, 0, width, radius, width, height - radius,
            width - radius, height, radius, height, 0, height - radius, 0, radius,
        ]

    def _build_insights(self):
        panel = tk.Frame(
            self.overview_content, bg="white", padx=18, pady=14, highlightthickness=1,
            highlightbackground="#E7ECF3",
        )
        panel.pack(fill="x", padx=32, pady=(0, 15))
        tk.Label(
            panel,
            text="Business insights",
            bg="white",
            fg=self.NAVY,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 8))
        self.insights_container = tk.Frame(panel, bg="white")
        self.insights_container.pack(fill="x")

    def _build_charts(self):
        self.chart_grid = tk.Frame(self.overview_content, bg=self.BACKGROUND)
        self.chart_grid.pack(fill="both", expand=True, padx=32, pady=(0, 28))
        self.chart_grid.grid_columnconfigure(0, weight=1, uniform="charts")
        self.chart_grid.grid_columnconfigure(1, weight=1, uniform="charts")

    def _parse_filter_date(self, value, label):
        value = value.strip()
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError("{} must use YYYY-MM-DD format.".format(label))

    def _apply_filters(self):
        try:
            start_date = self._parse_filter_date(self.start_var.get(), "From date")
            end_date = self._parse_filter_date(self.end_var.get(), "To date")
            filtered = self.analyzer.filter_records(
                self.data.records,
                start_date=start_date,
                end_date=end_date,
                category=self.category_var.get(),
                product_query=self.product_var.get(),
            )
        except ValueError as error:
            messagebox.showerror("Invalid filter", str(error), parent=self.root)
            return
        self.filtered_records = filtered
        self._refresh_overview()
        self._refresh_status()

    def _reset_filters(self):
        self.start_var.set("")
        self.end_var.set("")
        self.category_var.set("All Categories")
        self.product_var.set("")
        self._apply_filters()

    def _refresh_overview(self):
        if not hasattr(self, "kpi_values"):
            return
        try:
            start_date = self._parse_filter_date(self.start_var.get(), "From date")
            end_date = self._parse_filter_date(self.end_var.get(), "To date")
            self.filtered_records = self.analyzer.filter_records(
                self.data.records,
                start_date=start_date,
                end_date=end_date,
                category=self.category_var.get(),
                product_query=self.product_var.get(),
            )
        except ValueError:
            self.filtered_records = []

        kpis = self.analyzer.calculate_kpis(self.filtered_records)
        self.kpi_values["revenue"].configure(
            text="{} {:,.2f}".format(self.CURRENCY, kpis["revenue"])
        )
        self.kpi_values["orders"].configure(text="{:,}".format(kpis["orders"]))
        self.kpi_values["units_sold"].configure(text="{:,}".format(kpis["units_sold"]))
        self.kpi_values["average_order_value"].configure(
            text="{} {:,.2f}".format(self.CURRENCY, kpis["average_order_value"])
        )
        self._refresh_insights()
        self._refresh_charts()

    def _refresh_insights(self):
        for widget in self.insights_container.winfo_children():
            widget.destroy()
        insights = self.analyzer.business_insights(self.filtered_records)
        for index, insight in enumerate(insights):
            tk.Label(
                self.insights_container,
                text="\u2022  " + insight,
                bg="white",
                fg="#334155",
                font=("Segoe UI", 9),
                anchor="w",
                justify="left",
            ).grid(row=index // 2, column=index % 2, sticky="ew", padx=(0, 14), pady=3)
        self.insights_container.grid_columnconfigure(0, weight=1)
        self.insights_container.grid_columnconfigure(1, weight=1)

    def _refresh_charts(self):
        for widget in self.chart_grid.winfo_children():
            widget.destroy()
        charts = [
            ("monthly_revenue_chart", "Monthly revenue"),
            ("category_sales_chart", "Category sales"),
            ("category_distribution_chart", "Category distribution"),
            ("top_products_chart", "Top products"),
            ("daily_sales_chart", "Daily trend"),
        ]
        for index, (method_name, _label) in enumerate(charts):
            chart_frame = tk.Frame(
                self.chart_grid,
                bg="white",
                highlightthickness=1,
                highlightbackground="#E7ECF3",
            )
            chart_frame.grid(
                row=index // 2,
                column=index % 2,
                sticky="nsew",
                padx=(0, 12),
                pady=(0, 12),
            )
            figure = getattr(self.chart_generator, method_name)(
                self.filtered_records, self.analyzer
            )
            chart_canvas = FigureCanvasTkAgg(figure, master=chart_frame)
            chart_canvas.draw()
            chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def _show_records(self):
        self._set_active_nav("Sales records")
        self._clear_page()
        self._page_header(
            "Sales records",
            "Browse the records included in the current filtered analysis.",
        )
        controls = tk.Frame(self.page_container, bg=self.BACKGROUND)
        controls.pack(fill="x", padx=32, pady=(0, 12))
        tk.Label(
            controls,
            text="Showing {} filtered record(s)".format(len(self.filtered_records)),
            bg=self.BACKGROUND,
            fg=self.MUTED,
            font=("Segoe UI", 9),
        ).pack(side="left")
        tk.Button(
            controls,
            text="Export filtered CSV",
            command=self._export_csv,
            bg=self.ACCENT,
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="flat",
            padx=14,
            pady=8,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="right")

        table_frame = tk.Frame(
            self.page_container,
            bg="white",
            highlightthickness=1,
            highlightbackground="#E7ECF3",
        )
        table_frame.pack(fill="both", expand=True, padx=32, pady=(0, 26))
        columns = SalesData.REQUIRED_COLUMNS
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        vertical = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        vertical.pack(side="right", fill="y")
        horizontal.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)

        widths = {
            "Order_ID": 105,
            "Order_Date": 112,
            "Product_Name": 180,
            "Category": 135,
            "Quantity": 85,
            "Unit_Price": 105,
            "Total_Amount": 115,
            "Payment_Mode": 130,
        }
        for column in columns:
            tree.heading(column, text=column.replace("_", " "))
            tree.column(column, width=widths[column], minwidth=75, anchor="w")
        for record in self.filtered_records:
            values = []
            for column in columns:
                value = record[column]
                values.append(value.isoformat() if isinstance(value, date) else value)
            tree.insert("", "end", values=values)

    def _upload_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select a retail sales CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            parent=self.root,
        )
        if not file_path:
            return
        candidate = SalesData()
        try:
            count = candidate.load_csv(file_path)
        except (OSError, UnicodeError, ValueError, csv.Error) as error:
            messagebox.showerror("Could not load CSV", str(error), parent=self.root)
            return
        self.data = candidate
        self.start_var.set("")
        self.end_var.set("")
        self.category_var.set("All Categories")
        self.product_var.set("")
        self._update_category_options()
        self.filtered_records = self.data.records
        if self.active_page == "Overview":
            self._refresh_overview()
        else:
            self._show_records()
        self._refresh_status()
        messagebox.showinfo(
            "CSV loaded",
            "Loaded {:,} valid record(s). Skipped {:,} invalid row(s).".format(
                count, self.data.invalid_rows
            ),
            parent=self.root,
        )

    def _export_csv(self):
        if not self.filtered_records:
            messagebox.showwarning(
                "Nothing to export",
                "No sales records match the current filters.",
                parent=self.root,
            )
            return
        file_path = filedialog.asksaveasfilename(
            title="Export filtered sales",
            defaultextension=".csv",
            initialfile="filtered_sales_report.csv",
            filetypes=[("CSV files", "*.csv")],
            parent=self.root,
        )
        if not file_path:
            return
        try:
            SalesData.export_csv(file_path, self.filtered_records)
        except OSError as error:
            messagebox.showerror("Export failed", str(error), parent=self.root)
            return
        self.status_var.set(
            "Exported {:,} filtered record(s) to {}".format(
                len(self.filtered_records), Path(file_path).name
            )
        )
        messagebox.showinfo(
            "Report exported",
            "Exported {:,} filtered record(s).".format(len(self.filtered_records)),
            parent=self.root,
        )

    def _refresh_status(self):
        self.status_var.set(
            "Dataset: {:,} valid record(s)  |  {:,} invalid row(s) skipped  |  "
            "{:,} record(s) match filters".format(
                len(self.data.records),
                self.data.invalid_rows,
                len(self.filtered_records),
            )
        )
