import pandas as pd
import re
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates

def convert_seconds_to_datetime(initial_time, time_seconds):
    initial_datetime = datetime.strptime(initial_time, "%H:%M:%S %d/%m/%Y")
    return [initial_datetime + timedelta(seconds=t) for t in time_seconds]

def parse_log(file_path):
    df = pd.read_csv(file_path, sep=",")
    print(df)
    
    
def load_log(path):
    """
    Load the cryostat log file into a pandas DataFrame.
    Converts timestamps and numeric data, replaces '-' with NaN.
    """
    df = pd.read_csv(
        path,
        na_values=["-"],         # Convert "-" → NaN
        parse_dates=["Timestamp"],
        dayfirst=True            # Your format is dd/mm/yyyy
    )

    # Convert all non-timestamp columns to numeric where possible
    for col in df.columns:
        if col != "Timestamp":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
    # return {col: df[col].to_numpy() for col in df.columns}

