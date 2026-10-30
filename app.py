import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Olist | Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown("""
<style>
    .stApp {
        background-color: #0b1120;
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stMetric"] {
        background-color: #172033;
        border: 1px solid #263449;
        padding: 18px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8;
    }

    h1, h2, h3 {
        color: #f8fafc;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 15px;
    }

    div[data-testid="stTabs"] button {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data():
    orders = pd.read_csv(DATA_DIR / "order_analysis.csv")
    products = pd.read_csv(DATA_DIR / "product_analysis.csv")
    kpis = pd.read_csv(DATA_DIR / "business_kpis.csv")

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )

    for col in [
        "total_payment",
        "review_score",
        "delivery_days",
        "delivery_delay_days"
    ]:
        if col in orders.columns:
            orders[col] = pd.to_numeric(
                orders[col], errors="coerce"
            )

    for col in ["price", "freight_value"]:
        if col in products.columns:
            products[col] = pd.to_numeric(
                products[col], errors="coerce"
            )

    orders = orders.drop_duplicates(subset=["order_id"])

    return orders, products, kpis


try:
    orders, products, kpis = load_data()
except Exception as error:
    st.error(f"Could not load project datasets: {error}")
    st.info(
        "Check that all three CSV files exist inside data/processed/."
    )
    st.stop()

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def brl(value):
    return f"R$ {value:,.2f}"


def compact_brl(value):
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"R$ {value / 1_000:.2f}K"
    return brl(value)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("📊 OLIST ANALYTICS")
st.sidebar.caption("Business Intelligence Dashboard")
st.sidebar.divider()

st.sidebar.subheader("Dashboard Filters")

valid_dates = orders["order_purchase_timestamp"].dropna()

if valid_dates.empty:
    st.error("No valid order purchase dates found.")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_range = st.sidebar.date_input(
    "Purchase date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

status_options = sorted(
    orders["order_status"].dropna().unique().tolist()
)

selected_status = st.sidebar.multiselect(
    "Order status",
    options=status_options,
    default=status_options
)

state_options = sorted(
    orders["customer_state"].dropna().unique().tolist()
)

selected_states = st.sidebar.multiselect(
    "Customer state",
    options=state_options,
    default=state_options
)

filtered = orders[
    (orders["order_purchase_timestamp"].dt.date >= start_date) &
    (orders["order_purchase_timestamp"].dt.date <= end_date)
].copy()

if selected_status:
    filtered = filtered[
        filtered["order_status"].isin(selected_status)
    ]
else:
    filtered = filtered.iloc[0:0]

if selected_states:
    filtered = filtered[
        filtered["customer_state"].isin(selected_states)
    ]
else:
    filtered = filtered.iloc[0:0]

# ============================================================
# HEADER
# ============================================================

st.title("📊 Olist E-Commerce Intelligence")

st.markdown(
    '<p class="subtitle">Interactive business performance and '
    'exploratory analytics dashboard</p>',
    unsafe_allow_html=True
)

st.caption(
    f"Analysis period: {start_date} to {end_date} | "
    "Dataset: Brazilian E-Commerce Public Dataset by Olist"
)

st.divider()

# ============================================================
# KPI CALCULATIONS
# ============================================================

total_orders = filtered["order_id"].nunique()
total_customers = filtered["customer_id"].nunique()
total_revenue = filtered["total_payment"].sum()

average_order_value = (
    total_revenue / total_orders if total_orders else 0
)

average_review = filtered["review_score"].mean()
average_delivery = filtered["delivery_days"].mean()

delivered_orders = (
    filtered["order_status"].eq("delivered").sum()
)

cancelled_orders = (
    filtered["order_status"].eq("canceled").sum()
)

# ============================================================
# KPI CARDS
# ============================================================

st.subheader("Executive Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Orders", f"{total_orders:,}")
c2.metric("Customers", f"{total_customers:,}")

c3.metric(
    "Total Revenue",
    compact_brl(total_revenue),
    help=f"Full revenue value: {brl(total_revenue)}"
)

c4.metric(
    "Average Order Value",
    brl(average_order_value)
)

c5, c6, c7, c8 = st.columns(4)

c5.metric("Delivered Orders", f"{delivered_orders:,}")
c6.metric("Cancelled Orders", f"{cancelled_orders:,}")

c7.metric(
    "Average Review",
    f"{average_review:.2f}/5"
    if pd.notna(average_review) else "N/A"
)

c8.metric(
    "Average Delivery",
    f"{average_delivery:.1f} days"
    if pd.notna(average_delivery) else "N/A"
)

st.divider()

# ============================================================
# TABS
# ============================================================

overview_tab, sales_tab, product_tab, customer_tab, delivery_tab, data_tab = st.tabs([
    "📈 Overview",
    "💰 Sales Analytics",
    "📦 Product Analytics",
    "👥 Customer Analytics",
    "🚚 Delivery & Reviews",
    "📥 Data Explorer"
])

# ============================================================
# OVERVIEW
# ============================================================

with overview_tab:

    st.subheader("Business Performance Overview")

    left, right = st.columns(2)

    with left:
        status_data = (
            filtered["order_status"]
            .value_counts()
            .rename_axis("Order Status")
            .reset_index(name="Orders")
        )

        if not status_data.empty:
            fig = px.pie(
                status_data,
                names="Order Status",
                values="Orders",
                hole=0.55,
                title="Order Status Distribution",
                template="plotly_dark"
            )

            fig.update_traces(
                textinfo="none",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Orders: %{value:,}<br>"
                    "Share: %{percent:.2%}"
                    "<extra></extra>"
                )
            )

            fig.update_layout(
                legend_title_text="Order Status"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No order status data available.")

    with right:
        state_data = (
            filtered.groupby("customer_state", as_index=False)
            .agg(Orders=("order_id", "nunique"))
            .sort_values("Orders", ascending=False)
            .head(12)
        )

        fig = px.bar(
            state_data,
            x="customer_state",
            y="Orders",
            title="Top Customer States",
            labels={
                "customer_state": "State",
                "Orders": "Orders"
            },
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# SALES ANALYTICS
# ============================================================

with sales_tab:

    st.subheader("Sales and Revenue Trends")

    sales = filtered.dropna(
        subset=["order_purchase_timestamp"]
    ).copy()

    if not sales.empty:
        sales["Month"] = (
            sales["order_purchase_timestamp"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly = (
            sales.groupby("Month", as_index=False)
            .agg(
                Revenue=("total_payment", "sum"),
                Orders=("order_id", "nunique")
            )
        )

        left, right = st.columns(2)

        with left:
            fig = px.line(
                monthly,
                x="Month",
                y="Revenue",
                markers=True,
                title="Monthly Revenue",
                template="plotly_dark"
            )

            fig.update_traces(
                hovertemplate=(
                    "Month: %{x}<br>"
                    "Revenue: R$ %{y:,.2f}"
                    "<extra></extra>"
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig = px.bar(
                monthly,
                x="Month",
                y="Orders",
                title="Monthly Orders",
                template="plotly_dark"
            )

            st.plotly_chart(fig, use_container_width=True)

        fig = px.area(
            monthly,
            x="Month",
            y="Revenue",
            title="Revenue Growth Trend",
            template="plotly_dark"
        )

        fig.update_traces(
            hovertemplate=(
                "Month: %{x}<br>"
                "Revenue: R$ %{y:,.2f}"
                "<extra></extra>"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No sales records match the selected filters.")

# ============================================================
# PRODUCT ANALYTICS
# ============================================================

with product_tab:

    st.subheader("Product and Category Performance")

    category_data = (
        products.groupby("product_category_name", dropna=False)
        .agg(
            Revenue=("price", "sum"),
            Items=("order_item_id", "count"),
            Average_Price=("price", "mean")
        )
        .reset_index()
    )

    category_data["product_category_name"] = (
        category_data["product_category_name"]
        .fillna("Unknown")
    )

    category_data = category_data.sort_values(
        "Revenue", ascending=False
    ).head(15)

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            category_data.sort_values("Revenue"),
            x="Revenue",
            y="product_category_name",
            orientation="h",
            title="Top 15 Categories by Item Revenue",
            labels={
                "Revenue": "Item Revenue (BRL)",
                "product_category_name": "Category"
            },
            template="plotly_dark"
        )

        fig.update_traces(
            hovertemplate=(
                "Category: %{y}<br>"
                "Revenue: R$ %{x:,.2f}"
                "<extra></extra>"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            category_data.sort_values(
                "Items", ascending=False
            ),
            x="product_category_name",
            y="Items",
            title="Items Sold by Category",
            template="plotly_dark"
        )

        fig.update_layout(xaxis_tickangle=-45)

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Category Performance Table")

    st.dataframe(
        category_data,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# CUSTOMER ANALYTICS
# ============================================================

with customer_tab:

    st.subheader("Customer Distribution")

    customer_data = (
        filtered.groupby("customer_state", as_index=False)
        .agg(
            Customers=("customer_id", "nunique"),
            Orders=("order_id", "nunique"),
            Revenue=("total_payment", "sum")
        )
        .sort_values("Customers", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            customer_data.head(15),
            x="customer_state",
            y="Customers",
            title="Customers by State",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.scatter(
            customer_data,
            x="Customers",
            y="Revenue",
            size="Orders",
            hover_name="customer_state",
            title="Customer Count vs Revenue",
            template="plotly_dark"
        )

        fig.update_traces(
            hovertemplate=(
                "State: %{hovertext}<br>"
                "Customers: %{x:,}<br>"
                "Revenue: R$ %{y:,.2f}"
                "<extra></extra>"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        customer_data,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# DELIVERY AND REVIEWS
# ============================================================

with delivery_tab:

    st.subheader("Logistics and Customer Satisfaction")

    left, right = st.columns(2)

    with left:
        delivery_data = filtered.dropna(
            subset=["delivery_days"]
        )

        fig = px.histogram(
            delivery_data,
            x="delivery_days",
            nbins=30,
            title="Delivery Time Distribution",
            labels={"delivery_days": "Delivery Days"},
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        review_data = (
            filtered["review_score"]
            .dropna()
            .value_counts()
            .sort_index()
            .rename_axis("Review Score")
            .reset_index(name="Count")
        )

        fig = px.bar(
            review_data,
            x="Review Score",
            y="Count",
            title="Customer Review Distribution",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

    if "delivery_delay_days" in filtered.columns:
        delay_data = filtered.dropna(
            subset=["delivery_delay_days"]
        )

        fig = px.histogram(
            delay_data,
            x="delivery_delay_days",
            nbins=30,
            title="Delivery Difference vs Estimated Date",
            labels={
                "delivery_delay_days":
                    "Actual minus Estimated Days"
            },
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Delivery difference is based on the project's existing "
        "delivery_delay_days calculation. Negative values indicate "
        "delivery before the estimated date."
    )

# ============================================================
# DATA EXPLORER AND EXPORTS
# ============================================================

with data_tab:

    st.subheader("Explore Filtered Order Data")

    st.write(f"Records available: {len(filtered):,}")

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇ Download Filtered Orders CSV",
        data=csv_data,
        file_name="olist_filtered_orders.csv",
        mime="text/csv"
    )

    product_csv = products.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇ Download Product Analysis CSV",
        data=product_csv,
        file_name="olist_product_analysis.csv",
        mime="text/csv"
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Olist E-Commerce Business Intelligence Dashboard | "
    "Built with Python, Streamlit, Pandas and Plotly | "
    "CodeAlpha Data Analytics Internship"
)
