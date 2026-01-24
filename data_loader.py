import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data(file_path_or_buffer):
    """
    Loads data from a CSV or Excel file.
    Supports both file paths (str) and uploaded file buffers.
    """
    try:
        if isinstance(file_path_or_buffer, str):
            if file_path_or_buffer.endswith('.csv'):
                return pd.read_csv(file_path_or_buffer)
            elif file_path_or_buffer.endswith(('.xls', '.xlsx')):
                return pd.read_excel(file_path_or_buffer)
        else:
            # Streamlit UploadedFile object
            if file_path_or_buffer.name.endswith('.csv'):
                return pd.read_csv(file_path_or_buffer)
            elif file_path_or_buffer.name.endswith(('.xls', '.xlsx')):
                return pd.read_excel(file_path_or_buffer)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None
    return None

def get_dataset_overview(df):
    """
    Returns a dictionary containing key dataset metrics.
    """
    if df is None:
        return {}
    
    buffer_memory = df.memory_usage(deep=True).sum()
    memory_usage_mb = buffer_memory / 1024 ** 2
    
    overview = {
        "n_rows": df.shape[0],
        "n_columns": df.shape[1],
        "missing_values": df.isnull().sum().sum(),
        "duplicate_rows": df.duplicated().sum(),
        "memory_usage_mb": round(memory_usage_mb, 2),
        "column_types": df.dtypes.value_counts().to_dict()
    }
    return overview
