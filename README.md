# Olist E-Commerce Business Intelligence Dashboard

An interactive business intelligence dashboard built with Python, Streamlit, Pandas and Plotly as part of the CodeAlpha Data Analytics Internship.

The dashboard explores the Brazilian E-Commerce Public Dataset by Olist and presents business performance through interactive charts, KPIs and filters.

## Project Objectives

- Monitor overall e-commerce business performance.
- Explore order and revenue trends over time.
- Identify high-performing product categories.
- Understand customer distribution across Brazilian states.
- Analyze delivery performance and customer reviews.
- Allow users to filter and export order data.

## Technologies Used

- Python
- Pandas
- NumPy
- Streamlit
- Plotly

## Dashboard Features

### 1. Executive Overview
- Total orders
- Unique customers
- Total revenue
- Average order value
- Delivered and cancelled orders
- Average review score
- Average delivery time

### 2. Sales Analytics
- Monthly revenue trends
- Monthly order volume
- Revenue growth visualization

### 3. Product Analytics
- Top product categories by item revenue
- Items sold by category
- Category performance table

### 4. Customer Analytics
- Customer distribution by state
- Customer count versus revenue
- State-level customer and order metrics

### 5. Delivery & Reviews
- Delivery time distribution
- Customer review distribution
- Delivery difference versus estimated delivery date

### 6. Data Explorer
- Interactive filtered order records
- Download filtered orders as CSV
- Download product analysis as CSV

## Dataset

Brazilian E-Commerce Public Dataset by Olist.

Dataset source:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

The dashboard uses processed order, product and business KPI CSV files.

## Project Structure

```text
CodeAlpha-Data-Visualization/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── assets/
│
└── data/
    └── processed/
        ├── order_analysis.csv
        ├── product_analysis.csv
        └── business_kpis.csv
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Rachitesh29/CodeAlpha-Data-Visualization.git
cd CodeAlpha-Data-Visualization
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

http://localhost:8501

## Important Metric Notes

- The revenue KPI is calculated from the filtered order dataset.
- Product category revenue is based on product item prices and uses the complete processed product dataset.
- These revenue measures have different calculation bases and should not be interpreted as identical.

## Author

Rachitesh Sharma

GitHub: https://github.com/Rachitesh29

Project: CodeAlpha Data Analytics Internship
