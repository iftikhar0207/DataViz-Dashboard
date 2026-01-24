
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ------------------------------------------------------------------------------
# 1. Page Configuration & Styling
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Groceries Market Analysis",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional look
st.markdown("""
<style>
    /* Main container styling */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    /* Card styling for KPIs */
    .kpi-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    .kpi-title {
        color: #6c757d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .kpi-value {
        color: #212529;
        font-size: 1.8rem;
        font-weight: 700;
    }
    /* Chart container styling */
    .chart-container {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f1f3f6;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. Data Loading & Preprocessing
# ------------------------------------------------------------------------------
@st.cache_data
def load_and_process_data():
    """Reads the CSV, converts dates, and creates additional time features."""
    try:
        df = pd.read_csv("Groceries_dataset.csv")
        
        # Convert Date column (format is dd-mm-yyyy)
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
        
        # Drop rows with invalid dates if any
        df = df.dropna(subset=['Date'])
        
        # Determine "Transaction/Basket" ID
        # In this dataset, a basket is defined by unique combination of Member_number + Date
        df['Transaction_ID'] = df['Member_number'].astype(str) + "_" + df['Date'].astype(str)
        
        # Extract date features
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month_name()
        df['DayOfWeek'] = df['Date'].dt.day_name()
        df['Week'] = df['Date'].dt.isocalendar().week
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df_raw = load_and_process_data()

if df_raw.empty:
    st.stop()

# ------------------------------------------------------------------------------
# 3. Sidebar - Navigation & Filters
# ------------------------------------------------------------------------------
st.sidebar.header("Navigation")
page_selection = st.sidebar.radio("Go to", ["Overview", "Deep Dive", "Advanced Analysis", "Data Explorer"])

st.sidebar.markdown("---")
st.sidebar.header("Filters")

# Date Filter
min_date = df_raw['Date'].min()
max_date = df_raw['Date'].max()

try:
    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
except ValueError:
    st.sidebar.error("Please select a valid date range.")
    start_date, end_date = min_date, max_date

# Categorical Filter (Items)
all_items = sorted(df_raw['itemDescription'].unique())
selected_items = st.sidebar.multiselect(
    "Filter by Item (Optional)",
    options=all_items,
    default=[]
)

# Apply Filters
mask = (df_raw['Date'] >= pd.to_datetime(start_date)) & (df_raw['Date'] <= pd.to_datetime(end_date))
if selected_items:
    mask = mask & (df_raw['itemDescription'].isin(selected_items))

df_filtered = df_raw.loc[mask]

# ------------------------------------------------------------------------------
# 4. Page Content: Overview
# ------------------------------------------------------------------------------
if page_selection == "Overview":
    st.title("📊 Retail Dashboard: Overview")
    st.markdown("High-level performance metrics and sales trends.")
    
    # --- KPIs ---
    total_sales_count = len(df_filtered)
    unique_customers = df_filtered['Member_number'].nunique()
    total_transactions = df_filtered['Transaction_ID'].nunique()
    
    # Avoid division by zero
    avg_items_per_basket = total_sales_count / total_transactions if total_transactions > 0 else 0
    
    # Layout 4 KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    def kpi_card(title, value, col):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    kpi_card("Total Items Sold", f"{total_sales_count:,}", col1)
    kpi_card("Total Transactions", f"{total_transactions:,}", col2)
    kpi_card("Unique Customers", f"{unique_customers:,}", col3)
    kpi_card("Avg Items / Basket", f"{avg_items_per_basket:.2f}", col4)
    
    st.markdown("---")
    
    # --- Charts ---
    c1, c2 = st.columns((2, 1))
    
    with c1:
        st.subheader("📈 Sales Trend Over Time")
        # Aggregate by Date (Frequency = Monthly or Daily depending on range)
        sales_over_time = df_filtered.groupby('Date').size().reset_index(name='Items Sold')
        
        # Decide rolling average or resampling for cleaner chart if data is dense
        fig_line = px.line(sales_over_time, x='Date', y='Items Sold', 
                           title="Daily Sales Volume",
                           template="plotly_white",
                           line_shape='spline')
        fig_line.update_traces(line_color='#1f77b4', line_width=2)
        fig_line.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_line, use_container_width=True)
        
    with c2:
        st.subheader("🏆 Top 10 Best-Selling Items")
        top_items = df_filtered['itemDescription'].value_counts().head(10).reset_index()
        top_items.columns = ['Item', 'Count']
        
        fig_bar = px.bar(top_items, x='Count', y='Item', orientation='h',
                         title="Top 10 Items",
                         text='Count',
                         template="plotly_white",
                         color='Count',
                         color_continuous_scale='Blues')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, showlegend=False, 
                              margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- Insights Section ---
    st.markdown("### 💡 Key Insights")
    st.info(f"""
    - The dataset covers sales from **{start_date.strftime('%Y-%m-%d')}** to **{end_date.strftime('%Y-%m-%d')}**.
    - The most popular item in this period is **{top_items.iloc[0]['Item']}**.
    - On average, customers purchase **{avg_items_per_basket:.1f}** items per visit.
    """)

# ------------------------------------------------------------------------------
# 5. Page Content: Deep Dive
# ------------------------------------------------------------------------------
elif page_selection == "Deep Dive":
    st.title("🔍 Deep Dive Analysis")
    st.markdown("Detailed breakdown of customer behavior and patterns.")
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        st.subheader("📅 Weekly Activity Pattern")
        # Order days correctly
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        day_counts = df_filtered['DayOfWeek'].value_counts().reindex(days_order).reset_index()
        day_counts.columns = ['Day', 'Transactions']
        
        fig_day = px.bar(day_counts, x='Day', y='Transactions',
                         title="Transactions by Day of Week",
                         template="plotly_white",
                         color_discrete_sequence=['#2ca02c'])
        st.plotly_chart(fig_day, use_container_width=True)
        
    with col_d2:
        st.subheader("📅 Monthly Seasonality")
        # Aggregate by Month
        months_order = ["January", "February", "March", "April", "May", "June", 
                        "July", "August", "September", "October", "November", "December"]
        
        month_counts = df_filtered['Month'].value_counts().reindex(months_order).reset_index()
        month_counts.columns = ['Month', 'Transactions']
        
        fig_month = px.area(month_counts, x='Month', y='Transactions',
                            title="Transactions by Month (Seasonality)",
                            template="plotly_white",
                            color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig_month, use_container_width=True)

    st.markdown("---")
    st.subheader("👥 Customer Loyalty Analysis")
    
    # Calculate purchases per member
    member_counts = df_filtered.groupby('Member_number').size().reset_index(name='Total Purchases')
    
    c3, c4 = st.columns(2)
    with c3:
        fig_hist = px.histogram(member_counts, x='Total Purchases', nbins=20,
                                title="Distribution of Purchases per Customer",
                                template="plotly_white",
                                labels={'Total Purchases': 'Number of Items Purchased'},
                                color_discrete_sequence=['#9467bd'])
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with c4:
        st.markdown("""
        **Interpretation:**
        - This chart shows how many items customers typically buy over the selected period.
        - A skew to the left indicates most customers make few purchases, while a long tail to the right indicates loyal "power users".
        """)
        top_customer = member_counts.sort_values(by='Total Purchases', ascending=False).iloc[0]
        st.metric("Top Customer ID", str(top_customer['Member_number']))
        st.metric("Top Customer Purchases", int(top_customer['Total Purchases']))

# ------------------------------------------------------------------------------
# 6. Page Content: Advanced Analysis (Bivariate & Multivariate)
# ------------------------------------------------------------------------------
elif page_selection == "Advanced Analysis":
    st.title("🔬 Advanced Analysis")
    st.markdown("Bivariate and multivariate analysis to uncover deeper relationships.")
    
    # --- 1. Customer Segmentation (Bivariate) ---
    st.subheader("1. Customer Segmentation: Visits vs. Basket Size")
    st.markdown("Are frequent visitors buying more or less per trip?")
    
    # Calculate metrics per member
    customer_metrics = df_filtered.groupby(['Member_number']).agg(
        Total_Visits=('Transaction_ID', 'nunique'),
        Total_Items=('itemDescription', 'count')
    ).reset_index()
    customer_metrics['Avg_Basket_Size'] = customer_metrics['Total_Items'] / customer_metrics['Total_Visits']
    
    fig_scatter = px.scatter(
        customer_metrics, 
        x='Total_Visits', 
        y='Avg_Basket_Size',
        size='Total_Items',
        color='Total_Items',
        title="Customer Segments: Frequency vs. Basket Size",
        hover_data=['Member_number'],
        template="plotly_white",
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.info("💡 **Insight:** Customers in the bottom-right are frequent shoppers but buy few items (Convenience shoppers). Top-left are bulk buyers (Stock-up shoppers).")

    st.markdown("---")

    col_a1, col_a2 = st.columns(2)
    
    # --- 2. Heatmap: Item vs Day (Bivariate) ---
    with col_a1:
        st.subheader("2. Product Trends by Day")
        st.markdown("When are top products most likely to be sold?")
        
        # Get top 10 items
        top_10_list = df_filtered['itemDescription'].value_counts().head(10).index.tolist()
        df_top10 = df_filtered[df_filtered['itemDescription'].isin(top_10_list)]
        
        # Matrix: Item x Day
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heatmap_data = df_top10.pivot_table(index='itemDescription', columns='DayOfWeek', values='Member_number', aggfunc='count', fill_value=0)
        heatmap_data = heatmap_data.reindex(columns=days_order)
        
        fig_heat = px.imshow(
            heatmap_data,
            labels=dict(x="Day of Week", y="Product", color="Sales Count"),
            title="Top 10 Items Sales Heatmap",
            color_continuous_scale='RdBu_r'
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # --- 3. Market Basket Analysis (Multivariate) ---
    with col_a2:
        st.subheader("3. Market Basket Analysis")
        st.markdown("Which products are frequently bought together?")
        
        # Filter for top 15 items to keep matrix readable
        top_15_list = df_filtered['itemDescription'].value_counts().head(15).index.tolist()
        df_basket = df_filtered[df_filtered['itemDescription'].isin(top_15_list)]
        
        # Self-join to find pairs (this handles the multivariate aspect)
        df_basket = df_basket[['Transaction_ID', 'itemDescription']]
        
        # Create a cross-tabulation (One-hot encoding style per transaction)
        # This can be heavy, but for top 15 items it's very fast
        basket_matrix = pd.crosstab(df_basket['Transaction_ID'], df_basket['itemDescription'])
        
        # Co-occurrence matrix = A.T dot A
        # Convert to boolean (bought or not) then dot product
        basket_matrix = basket_matrix.clip(upper=1)
        co_occurrence = basket_matrix.T.dot(basket_matrix)
        
        # Zero out diagonal (item with itself) to highlight cross-product relationships
        import numpy as np
        np.fill_diagonal(co_occurrence.values, 0)
        
        fig_co = px.imshow(
            co_occurrence,
            labels=dict(x="Product A", y="Product B", color="Co-occurrences"),
            title="Co-occurrence Matrix (Top 15 Items)",
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_co, use_container_width=True)

# ------------------------------------------------------------------------------
# 7. Page Content: Data Explorer
# ------------------------------------------------------------------------------
elif page_selection == "Data Explorer":
    st.title("📂 Data Explorer")
    st.markdown("Filter and inspect the raw dataset.")
    
    st.dataframe(df_filtered.sort_values(by='Date', ascending=False), use_container_width=True)
    
    st.download_button(
        label="Download Filtered Data (CSV)",
        data=df_filtered.to_csv(index=False).encode('utf-8'),
        file_name='groceries_filtered.csv',
        mime='text/csv'
    )
