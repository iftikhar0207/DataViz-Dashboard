import streamlit as st
import pandas as pd
import os

# Import modules
from data_loader import load_data, get_dataset_overview
from stats_analysis import get_numerical_statistics, get_categorical_statistics, get_skewness_kurtosis
from visualizations import (plot_histogram, plot_box, plot_violin, plot_bar, 
                          plot_scatter, plot_correlation_heatmap, plot_pairplot)
from insights_engine import generate_automated_insights, detect_outliers_iqr
from report_generator import generate_text_report

# Page Configuration
st.set_page_config(
    page_title="Advanced EDA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2815/2815428.png", width=100)
    st.title("Groceries Analysis EDA")
    st.markdown("---")
    
    # Navigation
    page = st.radio("Navigation", [
        "📂 Data Overview",
        "📊 Descriptive Stats",
        "📈 Univariate Analysis",
        "🔗 Bivariate Analysis",
        "🧠 Multivariate Analysis",
        "🧾 Final Report"
    ])
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    

# Load Data logic
@st.cache_data
def get_main_dataframe():
   
    default_path = os.path.join(os.getcwd(), "Groceries_dataset.csv")
    if os.path.exists(default_path):
            return load_data(default_path)
    return None

df = get_main_dataframe()
df = df.copy()  # make a copy to avoid original mutations
df.columns = df.columns.astype(str)  # ensure all column names are strings

if df is not None:
    # 1. Data Overview
    if page == "📂 Data Overview":
        st.subheader("📂 Dataset Overview")
        
        overview = get_dataset_overview(df)
        
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.metric("Rows", overview['n_rows'])
        with c2: st.metric("Columns", overview['n_columns'])
        with c3: st.metric("Missing Values", overview['missing_values'])
        with c4: st.metric("Duplicates", overview['duplicate_rows'])
        with c5: st.metric("Memory (MB)", overview['memory_usage_mb'])
        
        st.markdown("### 📋 Data Preview")
        st.dataframe(df.head(100), use_container_width=True)
        
        with st.expander("Show Column Types"):
             column_types = {}
             for col, dtype in overview['column_types'].items():
                 column_types.setdefault(str(dtype), []).append(col)
             st.json(column_types)


    # 2. Descriptive Stats
    elif page == "📊 Descriptive Stats":
        st.subheader("📊 Descriptive Statistics")
        
        tab1, tab2 = st.tabs(["Numerical", "Categorical"])
        
        with tab1:
            st.markdown("#### Numerical Summary")
            st.dataframe(get_numerical_statistics(df), use_container_width=True)
            
            st.markdown("#### Skewness & Kurtosis")
            st.dataframe(get_skewness_kurtosis(df).T, use_container_width=True)
            
        with tab2:
            st.markdown("#### Categorical Summary")
            st.dataframe(get_categorical_statistics(df), use_container_width=True)

    # 3. Univariate Analysis
    elif page == "📈 Univariate Analysis":
        st.subheader("📈 Univariate Analysis")
        
        col_type = st.radio("Select Variable Type", ["Numerical", "Categorical"], horizontal=True)
        
        if col_type == "Numerical":
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            if num_cols:
                selected_col = st.selectbox("Select Column", num_cols)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(plot_histogram(df, selected_col), use_container_width=True)
                with c2:
                    st.plotly_chart(plot_box(df, selected_col), use_container_width=True)
                    
                st.info(f"Analysis: The histogram shows the frequency distribution of **{selected_col}**, while the boxplot highlights the median and potential outliers.")
            else:
                st.warning("No numerical columns found.")
                
        else:
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            if cat_cols:
                selected_col = st.selectbox("Select Column", cat_cols)
                st.plotly_chart(plot_bar(df, selected_col), use_container_width=True)
                st.info(f"Analysis: This bar chart displays the count of each category in **{selected_col}**.")
            else:
                st.warning("No categorical columns found.")

    # 4. Bivariate Analysis
    elif page == "🔗 Bivariate Analysis":
        st.subheader("🔗 Bivariate Analysis")
        
        plot_type = st.radio("Select Plot Type", ["Scatter Plot", "Correlation Heatmap"], horizontal=True)
        
        if plot_type == "Scatter Plot":
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(num_cols) >= 2:
                c1, c2, c3 = st.columns(3)
                x_col = c1.selectbox("X Axis", num_cols, index=0)
                y_col = c2.selectbox("Y Axis", num_cols, index=1)
                color_col = c3.selectbox("Color By (Optional)", [None] + df.columns.tolist())
                
                st.plotly_chart(plot_scatter(df, x_col, y_col, color=color_col), use_container_width=True)
            else:
                st.warning("Need at least 2 numerical columns.")
                
        elif plot_type == "Correlation Heatmap":
            st.plotly_chart(plot_correlation_heatmap(df), use_container_width=True)
            st.info("Analysis: The heatmap shows Pearson correlation coefficients. Values closer to 1 or -1 indicate strong linear relationships.")

    # 5. Multivariate Analysis
    elif page == "🧠 Multivariate Analysis":
        st.subheader("🧠 Multivariate Analysis")
        
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        if len(num_cols) > 1:
            selected_cols = st.multiselect("Select Columns for Pair Plot", num_cols, default=num_cols[:3])
            color_col = st.selectbox("Color By (Optional)", [None] + df.columns.tolist(), key="multi_color")
            
            if len(selected_cols) > 1:
                st.plotly_chart(plot_pairplot(df, selected_cols, color=color_col), use_container_width=True)
            else:
                st.warning("Please select at least 2 columns.")
        else:
            st.warning("Not enough numerical columns.")

    # 6. Final Report
    elif page == "🧾 Final Report":
        st.subheader("🧾 Final EDA Conclusion & Insights Report")
        
        with st.spinner("Generating Report..."):
            overview = get_dataset_overview(df)
            insights = generate_automated_insights(df)
            report_text = generate_text_report(df, overview, insights)
            
            st.text_area("Executive Summary", report_text, height=400)
            
            st.download_button(
                label="📥 Download Report as Text",
                data=report_text,
                file_name="EDA_Report.txt",
                mime="text/plain"
            )
            
            # Optional: Display Insights beautifully
            st.markdown("### 💡 Key Findings")
            for insight in insights:
                st.success(insight)

else:
    st.warning("Dataset not found. Please ensure 'synthetic_fraud_dataset.csv' exists in the project directory.")
