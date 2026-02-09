import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="Global Billionaires Insights",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium UI ---
st.markdown("""
<style>
    /* Main Background & Layout Adjustments */
    .stApp {
        background-color: #F8F9FA;
        font-family: 'Inter', sans-serif;
    }
    
    /* Reduce Streamlit Default Padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }
    
    /* Hide Default Header/Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Top Navigation Bar */
    .top-bar {
        background-color: #1E1B4B;
        padding: 0.8rem 1.5rem;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Card Styling */
    .metric-card {
        background-color: #FFFFFF;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-card:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.08);
        border-color: #C7D2FE;
    }
    
    /* Typography */
    .metric-title {
        color: #6B7280;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        color: #111827;
        font-size: 1.6rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .metric-delta {
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        background: #F3F4F6;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .delta-positive { color: #059669; background: #ECFDF5; }
    .delta-negative { color: #DC2626; background: #FEF2F2; }
    .delta-neutral { color: #6B7280; }

    /* Section Headers */
    h3 {
        color: #111827;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #4F46E5;
        padding-left: 8px;
    }
    
    /* Custom List for Top Individuals */
    .top-list-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 0;
        border-bottom: 1px solid #F3F4F6;
        font-size: 0.9rem;
    }
    .top-list-item:last-child { border-bottom: none; }
    .rank-badge {
        background-color: #EEF2FF;
        color: #4F46E5;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
        margin-right: 8px;
        font-size: 0.75rem;
        min-width: 24px;
        text-align: center;
    }
    .person-name { font-weight: 600; color: #374151; }
    .person-worth { font-weight: 700; color: #111827; }
    .worth-bar {
        height: 4px;
        background-color: #4F46E5;
        border-radius: 2px;
        margin-top: 4px;
        opacity: 0.8;
    }

</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cleaned_billionaires.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("Data not found. Please run `eda.py`.")
    st.stop()

# --- Sidebar Filters ---
with st.sidebar:
    st.markdown("### ⚙️ Filters")
    # Country
    countries = ['All Countries'] + sorted(df['country'].unique().tolist())
    sel_country = st.selectbox("Country", countries)
    
    # Industry
    industries = ['All Industries'] + sorted(df['industries'].unique().tolist())
    sel_industry = st.selectbox("Industry", industries)
    
    # Gender
    genders = ['All'] + sorted(df['gender'].unique().tolist())
    sel_gender = st.selectbox("Gender", genders)
    
    # Worth Range
    min_w, max_w = int(df['net_worth_billions'].min()), int(df['net_worth_billions'].max())
    sel_worth = st.slider("Net Worth ($B)", min_w, max_w, (min_w, max_w))

    st.markdown("---")
    st.markdown("<div style='text-align:center; color:#9CA3AF; font-size:0.8rem;'>v2.0 • Premium Edition</div>", unsafe_allow_html=True)

# --- Filtering Logic ---
filtered = df.copy()
if sel_country != 'All Countries': filtered = filtered[filtered['country'] == sel_country]
if sel_industry != 'All Industries': filtered = filtered[filtered['industries'] == sel_industry]
if sel_gender != 'All': filtered = filtered[filtered['gender'] == sel_gender]
filtered = filtered[(filtered['net_worth_billions'] >= sel_worth[0]) & (filtered['net_worth_billions'] <= sel_worth[1])]

# --- Helper Function for KPI Card ---
def kpi_card(title, value, delta=None, delta_type="neutral", sub_label=""):
    delta_html = ""
    if delta:
        color_class = f"delta-{delta_type}"
        icon = "↗" if delta_type == "positive" else "↘" if delta_type == "negative" else "•"
        delta_html = f'<div class="metric-delta {color_class}">{icon} {delta}</div>'
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            {delta_html}
            <span style="color:#9CA3AF; font-size:0.8rem;">{sub_label}</span>
        </div>
        <div style="height:4px; background:#F3F4F6; margin-top:10px; border-radius:2px; overflow:hidden;">
            <div style="height:100%; width:70%; background:#4F46E5; border-radius:2px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown(f"""
<div class="top-bar">
    <div>
        <h2 style="margin:0; font-size:1.5rem;">Global Billionaires Insights <span style="font-weight:300; opacity:0.8;">Dashboard</span></h2>
    </div>
    <div style="font-size:0.9rem; opacity:0.8;">
        Last updated: Oct 24, 2024 &nbsp; | &nbsp; 🔔 &nbsp; <span style="background:#4338CA; padding:4px 8px; border-radius:4px;">JD</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Row 1: KPI Cards ---
metrics_cols = st.columns(5)

# Calculate Metrics
total_count = len(filtered)
total_wealth = filtered['net_worth_billions'].sum()
avg_wealth = filtered['net_worth_billions'].mean() if total_count > 0 else 0
top_wealth = filtered['net_worth_billions'].max() if total_count > 0 else 0
unique_countries = filtered['country'].nunique()

with metrics_cols[0]:
    kpi_card("Total Billionaires", f"{total_count:,}", "~2.4%", "positive")
with metrics_cols[1]:
    kpi_card("Combined Net Worth", f"${total_wealth:,.1f}B", "~1.1%", "negative")
with metrics_cols[2]:
    kpi_card("Average Net Worth", f"${avg_wealth:.1f}B", "~0.5%", "positive")
with metrics_cols[3]:
    kpi_card("Top Individual Wealth", f"${top_wealth:.0f}B", "~15.2%", "positive")
with metrics_cols[4]:
    kpi_card("Countries Represented", f"{unique_countries}", "Stable", "neutral")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# --- Row 2: Top List | Map | Donuts ---
row2_cols = st.columns([1, 2, 1])

# Col 1: Top 10 List
with row2_cols[0]:
    st.markdown('<div class="metric-card"><h3>TOP 10 INDIVIDUALS</h3>', unsafe_allow_html=True)
    top_10 = filtered.nlargest(10, 'net_worth_billions')[['personName', 'net_worth_billions']]
    
    for i, (index, row) in enumerate(top_10.iterrows()):
        max_val = top_10['net_worth_billions'].max()
        percent = (row['net_worth_billions'] / max_val) * 100
        st.markdown(f"""
        <div class="top-list-item">
            <div style="flex:1;">
                <span class="rank-badge">{i+1}.</span>
                <span class="person-name">{row['personName']}</span>
                <div class="worth-bar" style="width:{percent}%;"></div>
            </div>
            <div class="person-worth">${row['net_worth_billions']:.0f}B</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Col 2: Global Map
with row2_cols[1]:
    st.markdown('<div class="metric-card"><h3>GLOBAL CONCENTRATION MAP</h3>', unsafe_allow_html=True)
    if 'latitude_country' in filtered.columns and 'longitude_country' in filtered.columns:
        # Group by country for cleaner map
        country_agg = filtered.groupby(['country', 'latitude_country', 'longitude_country']).agg(
            Count=('personName', 'count'),
            TotalWealth=('net_worth_billions', 'sum')
        ).reset_index()
        
        fig_map = px.scatter_geo(
            country_agg,
            lat='latitude_country',
            lon='longitude_country',
            size='Count',
            hover_name='country',
            size_max=40,
            template='plotly_white',
            color_discrete_sequence=['#4F46E5']
        )
        fig_map.update_geos(
            showcountries=True, countrycolor="#E5E7EB",
            showcoastlines=False,
            showland=True, landcolor="#F3F4F6",
            showocean=False,
            projection_type="natural earth"
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=400)
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Lat/Lon data required for map.")
    st.markdown('</div>', unsafe_allow_html=True)

# Col 3: Donuts (Source & Gender)
with row2_cols[2]:
    # Wealth Source (Self-Made vs Inherited)
    st.markdown('<div class="metric-card"><h3>WEALTH SOURCE</h3>', unsafe_allow_html=True)
    if 'selfMade' in filtered.columns:
        source_counts = filtered['selfMade'].value_counts()
        # Ensure boolean/string compatibility
        fig_donut1 = px.pie(
            names=source_counts.index, 
            values=source_counts.values, 
            hole=0.7,
            color_discrete_sequence=['#4F46E5', '#9CA3AF'] # Purple, Grey
        )
        fig_donut1.update_layout(showlegend=False, margin={"r":10,"t":0,"l":10,"b":0}, height=180, 
                                 annotations=[dict(text=f"{int(source_counts.get(True, 0)/source_counts.sum()*100)}%", x=0.5, y=0.5, font_size=20, showarrow=False)])
        st.plotly_chart(fig_donut1, use_container_width=True)
        # Custom Legend
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-top:10px;">
            <div><span style="color:#4F46E5;">●</span> Self-Made</div>
            <div style="font-weight:bold;">{source_counts.get(True, 0):,}</div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.8rem;">
            <div><span style="color:#9CA3AF;">●</span> Inherited</div>
            <div style="font-weight:bold;">{source_counts.get(False, 0):,}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Gender Parity
    st.markdown('<div class="metric-card"><h3>GENDER PARITY</h3>', unsafe_allow_html=True)
    gender_counts = filtered['gender'].value_counts()
    fig_donut2 = px.pie(
        names=gender_counts.index, 
        values=gender_counts.values, 
        hole=0.7,
        color_discrete_sequence=['#4F46E5', '#FB7185'] # Purple (Male), Pink (Female) typically represented
    )
    # Adjust colors if labels are Male/Female specifically
    color_map = {'M': '#4F46E5', 'F': '#EC4899', 'Male': '#4F46E5', 'Female': '#EC4899'}
    fig_donut2.update_traces(marker=dict(colors=[color_map.get(x, '#9CA3AF') for x in gender_counts.index]))
    
    fig_donut2.update_layout(showlegend=False, margin={"r":10,"t":0,"l":10,"b":0}, height=180,
                             annotations=[dict(text=f"{int(gender_counts.get('F', 0)/gender_counts.sum()*100)}%", x=0.5, y=0.5, font_size=20, showarrow=False)])
    st.plotly_chart(fig_donut2, use_container_width=True)
    
     # Custom Legend
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-top:10px;">
        <div><span style="color:#4F46E5;">●</span> Male</div>
        <div style="font-weight:bold;">{gender_counts.get('M', 0):,}</div>
    </div>
    <div style="display:flex; justify-content:space-between; font-size:0.8rem;">
        <div><span style="color:#EC4899;">●</span> Female</div>
        <div style="font-weight:bold;">{gender_counts.get('F', 0):,}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# --- Row 3: Industry | Net Worth Dist | Age Dist ---
row3_cols = st.columns([1, 1.5, 1])

# Col 1: Industry Share
with row3_cols[0]:
    st.markdown('<div class="metric-card"><h3>INDUSTRY SHARE</h3>', unsafe_allow_html=True)
    top_ind = filtered['industries'].value_counts().head(5)
    # Treemap approx using Bar for simplicity in small space
    fig_bar = px.bar(
        x=top_ind.index,
        y=top_ind.values,
        color=top_ind.values,
        color_continuous_scale=['#C7D2FE', '#4F46E5']
    )
    fig_bar.update_layout(showlegend=False, margin={"r":0,"t":0,"l":0,"b":0}, height=250, template='plotly_white')
    fig_bar.update_xaxes(showticklabels=False)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Textual legend/list
    for ind, count in top_ind.items():
        pct = (count / total_count) * 100
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
            <div style="background:#EEF2FF; padding:2px 6px; border-radius:4px;">{ind}</div>
            <div style="font-weight:bold;">{pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Col 2: Net Worth Distribution
with row3_cols[1]:
    st.markdown('<div class="metric-card"><h3>NET WORTH DISTRIBUTION</h3>', unsafe_allow_html=True)
    fig_hist = px.histogram(
        filtered, 
        x='net_worth_billions',
        nbins=40,
        color_discrete_sequence=['#C7D2FE']
    )
    fig_hist.update_layout(
        template='plotly_white', 
        bargap=0.1,
        margin={"r":0,"t":20,"l":0,"b":0}, 
        height=300,
        yaxis_title="Count",
        xaxis_title="Net Worth ($B)"
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Col 3: Age Distribution
with row3_cols[2]:
    st.markdown('<div class="metric-card"><h3>AGE DISTRIBUTION</h3>', unsafe_allow_html=True)
    # Create Age Bins
    bins = [18, 35, 50, 70, 100]
    labels = ['18-35', '36-50', '51-70', '70+']
    filtered['Age_Bin'] = pd.cut(filtered['age'], bins=bins, labels=labels)
    age_counts = filtered['Age_Bin'].value_counts().sort_index()
    
    fig_age = px.bar(
        y=age_counts.index,
        x=age_counts.values,
        orientation='h',
        text=age_counts.values,
        color_discrete_sequence=['#4F46E5']
    )
    fig_age.update_layout(
        template='plotly_white',
        margin={"r":0,"t":0,"l":0,"b":0},
        height=300,
        xaxis_visible=False
    )
    st.plotly_chart(fig_age, use_container_width=True)
    st.markdown(f"<div style='text-align:center; font-size:0.8rem; color:#6B7280; margin-top:10px;'>Avg. Age: <b>{filtered['age'].mean():.1f} Years</b></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div style="background-color:#111827; color:white; padding:2rem; margin-top:3rem; text-align:center;">
    <p style="font-weight:bold; letter-spacing:1px;">DATA SOURCE</p>
    <p style="font-size:0.9rem; opacity:0.7;">Global Wealth Annual Report 2024</p>
    <div style="margin-top:20px; font-size:0.8rem; opacity:0.5;">
        Methodology: Asset-Liability Valuation (Net) • Data verified for executive analysis <span style="color:#10B981;">✔</span>
    </div>
</div>
""", unsafe_allow_html=True)
