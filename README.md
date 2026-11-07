# Retail Sales Analytics Dashboard

A desktop dashboard for exploring retail sales stored in CSV files. The app
loads a sample dataset at startup and provides interactive filters, business
KPIs, Matplotlib visualizations, a record table, CSV upload, and filtered
report export.

## Objectives

- Read and validate structured retail sales data from CSV.
- Practice Python object-oriented programming and data analysis.
- Summarize sales with useful, dynamically calculated business metrics.
- Present trends and category/product comparisons in an accessible GUI.

## Technologies

- Python 3.10 or later
- Tkinter and ttk for the desktop interface
- Matplotlib for charts
- Python `csv` module for data loading and report export

No paid API, network service, Pandas, or NumPy dependency is required.

## Features

- Four KPIs: total revenue, distinct orders, product units sold, and average
  order value.
- Monthly and daily revenue trends, revenue by category, category distribution,
  and the five products with the highest unit sales.
- Date range, category, and product-name filters that update the KPIs, insights,
  and charts together.
- Automatic business insights based on the currently filtered records.
- CSV validation with clear required-column errors and skipped-row counts for
  rows with missing or invalid values.
- A searchable-by-filtering table view of the matching records.
- Export of the filtered records to a new CSV report.

## Project structure

```text
Retail_Sales_Dashboard/
├── main.py
├── sales_data.py
├── sales_analyzer.py
├── chart_generator.py
├── dashboard.py
├── data/
│   └── retail_sales.csv
├── assets/
├── requirements.txt
└── README.md
```

`assets/` is reserved for optional local project artwork; the application does
not require external images.

## Installation

Install Python 3.10 or later. Tkinter is included with most standard Windows
Python installers. From this project folder, create and activate a virtual
environment in PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run the app with the environment's interpreter
directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Run the application

```powershell
python main.py
```

The sample CSV is loaded automatically. Use **Upload CSV** in the sidebar to
choose another dataset or **Export filtered CSV** to save the records currently
included in the dashboard analysis.

## CSV format and sample data

The bundled `data/retail_sales.csv` contains 160 reproducible sample
transactions across Electronics, Clothing, Grocery, Furniture, and Accessories.
The required headers are:

```text
Order_ID, Order_Date, Product_Name, Category, Quantity, Unit_Price,
Total_Amount, Payment_Mode
```

Dates in uploaded files may use `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, or
`YYYY/MM/DD`. Quantity must be a positive whole number. Prices and amounts must
be finite, non-negative numbers. Invalid individual rows are skipped and
reported; a missing required column or a file with no valid rows is rejected.

## Object-oriented design

- **`SalesData`** encapsulates the validated records and is responsible for
  loading, checking, and exporting CSV data.
- **`SalesAnalyzer`** filters records and calculates KPIs, grouped sales, top
  products, and business insights.
- **`ChartGenerator`** turns analyzed records into consistently styled
  Matplotlib figures.
- **`DashboardApp`** owns the Tkinter interface and connects user actions to the
  data, analysis, and chart layers.

Each class has a clear responsibility and exposes methods used by the dashboard,
demonstrating classes, objects, constructors, encapsulated state, and separation
of responsibilities.
