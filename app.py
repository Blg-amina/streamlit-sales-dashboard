import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(
    page_title="AI Business Intelligence - Univ Ain Temouchent",
    page_icon=":bar_chart:",
    layout="wide",
)

# --- CUSTOM CSS (Dark Luxe Theme) ---
st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    body, .stApp { background-color: #0b1120; color: #e5e7eb; }
    .stMetric {
        border-radius: 1rem;
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    footer, header, #MainMenu { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- DATA LOADING & LOCALIZATION ---
@st.cache_data
def load_and_localize_data():
    # Loading raw data
    df = pd.read_excel(
        io="supermarkt_sales.xlsx",
        engine="openpyxl",
        sheet_name="Sales",
        skiprows=3,
        usecols="B:R",
        nrows=1000,
    )
    
    # 1. Localizing Cities (Algerian Market)
    city_map = {
        'Yangon': 'Ain Temouchent', 
        'Naypyitaw': 'Oran', 
        'Mandalay': 'Algiers'
    }
    df['City'] = df['City'].replace(city_map)

    # 2. Localizing Payment Methods
    payment_map = {
        'Cash': 'Cash (السيولة)', 
        'Ewallet': 'BaridiMob / Pay', 
        'Credit card': 'Edahabia / CIB'
    }
    df['Payment'] = df['Payment'].replace(payment_map)

    # 3. Time & Rating Engineering
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    df["Rating"] = df["Rating"].apply(lambda x: min(x, 5.0))
    
    return df

df = load_and_localize_data()

# --- SIDEBAR ---
sidebar = st.sidebar
try:
    logo = Image.open("assets/logo_univ.png")
    sidebar.image(logo, width=180)
except Exception:
    pass

sidebar.header("Academic Case Study")
sidebar.markdown("""
    **Institution:** University of Ain Temouchent  
    **Faculty:** Economics & Management  
    **Lecturer:** Amina Belaggoun
    """)
sidebar.markdown("---")

# Filters
city = sidebar.multiselect("Select City", options=df["City"].unique(), default=df["City"].unique())
customer_type = sidebar.multiselect("Customer Type", options=df["Customer_type"].unique(), default=df["Customer_type"].unique())
gender = sidebar.multiselect("Gender", options=df["Gender"].unique(), default=df["Gender"].unique())

sidebar.markdown("---")
sidebar.info("💡 **Data Note:** This simulation uses localized Algerian market data for strategic analysis.")

# --- FILTERING LOGIC ---
filtered_df = df.query("City == @city & Customer_type == @customer_type & Gender == @gender")

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# --- KPI METRICS ---
sales_total = filtered_df["Total"].sum()
average_rating = round(filtered_df["Rating"].mean(), 1)
average_sale = round(filtered_df["Total"].mean(), 2)

st.title("📊 AI Business Intelligence Dashboard")
st.markdown("#### Strategic Sales Analysis | Faculty of Economics - Ain Temouchent")

m1, m2, m3 = st.columns(3)
m1.metric("Total Revenue", f"{sales_total:,.2f} DZD")
m2.metric("Avg. Transaction", f"{average_sale:,.2f} DZD")
m3.metric("Avg. Satisfaction", f"{average_rating} / 5.0 ⭐")

st.markdown("---")

# --- VISUALIZATIONS ---
# Product Line Analysis
sales_by_product_line = (
    filtered_df.groupby(by=["Product line"], as_index=False)["Total"]
    .sum()
    .sort_values(by="Total", ascending=False)
)

fig_product_sales = px.bar(
    sales_by_product_line,
    x="Total",
    y="Product line",
    orientation="h",
    title="<b>Revenue by Product Category</b>",
    template="plotly_dark",
    color_discrete_sequence=["#2563eb"],
    labels={"Total": "Total (DZD)"}
)
fig_product_sales.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

# Hourly Analysis
sales_by_hour = filtered_df.groupby(by=["hour"], as_index=False)["Total"].sum()
fig_hourly_sales = px.line(
    sales_by_hour,
    x="hour",
    y="Total",
    title="<b>Sales Trend by Hour</b>",
    template="plotly_dark",
    labels={"Total": "Total (DZD)"}
)
fig_hourly_sales.update_traces(line_color="#10b981", line_width=3)
fig_hourly_sales.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

col1, col2 = st.columns(2)
col1.plotly_chart(fig_hourly_sales, use_container_width=True)
col2.plotly_chart(fig_product_sales, use_container_width=True)

# --- AI INSIGHTS ---
peak_hour = int(sales_by_hour.loc[sales_by_hour["Total"].idxmax(), "hour"])
top_sector = sales_by_product_line.loc[sales_by_product_line["Total"].idxmax(), "Product line"]

st.markdown("---")
st.header("🤖 AI Predictive Insights & Strategic Recommendations")
st.success(f"""
- **Peak Performance Window:** Analysis identifies **{peak_hour}:00** as the critical sales peak. *Recommendation: Optimize staffing levels during this window.*
- **Market Driver:** The **{top_sector}** category shows the highest growth potential. *Recommendation: Increase inventory depth for this sector.*
- **Strategic Note:** Transitioning to digital payments (BaridiMob/Edahabia) could reduce transaction friction and improve data accuracy.
""")