"""
Helper functions for Option Chain Analyzer
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Union


def format_number(num: Union[int, float]) -> str:
    """Format number with commas"""
    if pd.isna(num) or num is None:
        return "N/A"
    try:
        if isinstance(num, float) and num.is_integer():
            num = int(num)
        return f"{num:,}"
    except:
        return str(num)


def format_currency(value: Union[int, float]) -> str:
    """Format currency value"""
    if pd.isna(value) or value is None:
        return "₹0"
    try:
        if abs(value) >= 10000000:  # 1 Crore+
            return f"₹{value/10000000:.2f}Cr"
        elif abs(value) >= 100000:  # 1 Lakh+
            return f"₹{value/100000:.2f}L"
        elif abs(value) >= 1000:
            return f"₹{value:,.0f}"
        else:
            return f"₹{value:.2f}"
    except:
        return "₹0"


def get_color_for_value(value: float, thresholds: List[Tuple[float, str]]) -> str:
    """Get color based on value thresholds"""
    for threshold, color in thresholds:
        if value <= threshold:
            return color
    return thresholds[-1][1] if thresholds else "gray"


def get_verdict_color(verdict: str) -> str:
    """Get color for verdict"""
    colors = {
        "STRONG BULLISH": "#00cc66",
        "BULLISH": "#88dd88",
        "WEAK BULLISH": "#ccdd88",
        "NEUTRAL": "#ffaa00",
        "WEAK BEARISH": "#dd8866",
        "BEARISH": "#dd4444",
        "STRONG BEARISH": "#cc0000"
    }
    return colors.get(verdict, "gray")


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / abs(old_value)) * 100


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default value"""
    if denominator == 0 or pd.isna(denominator):
        return default
    return numerator / denominator


def get_strike_range(df: pd.DataFrame, atm_strike: float, range_pct: float = 0.05) -> Tuple[float, float]:
    """Get strike range around ATM"""
    lower = atm_strike * (1 - range_pct)
    upper = atm_strike * (1 + range_pct)
    return (lower, upper)


def filter_near_atm(df: pd.DataFrame, atm_strike: float, range_pct: float = 0.03) -> pd.DataFrame:
    """Filter strikes near ATM"""
    lower, upper = get_strike_range(df, atm_strike, range_pct)
    strikes = pd.to_numeric(df['STRIKE PRICE'], errors='coerce')
    mask = (strikes >= lower) & (strikes <= upper)
    return df[mask]


def get_top_n_strikes(df: pd.DataFrame, column: str, n: int = 5) -> List[Tuple[float, float]]:
    """Get top N strikes by column value"""
    values = pd.to_numeric(df[column], errors='coerce').fillna(0)
    strikes = pd.to_numeric(df['STRIKE PRICE'], errors='coerce')
    
    top_indices = values.nlargest(n).index
    result = []
    for idx in top_indices:
        if idx < len(strikes):
            result.append((float(strikes.iloc[idx]), float(values.iloc[idx])))
    return result


def calculate_bid_ask_spread(df: pd.DataFrame, side: str = 'x') -> pd.Series:
    """Calculate bid-ask spread"""
    bid_col = f'BID_{side}'
    ask_col = f'ASK_{side}'
    
    if bid_col in df.columns and ask_col in df.columns:
        bid = pd.to_numeric(df[bid_col], errors='coerce')
        ask = pd.to_numeric(df[ask_col], errors='coerce')
        return ask - bid
    return pd.Series([0] * len(df))


def is_valid_strike(strike: float) -> bool:
    """Check if strike is valid"""
    return not (pd.isna(strike) or strike <= 0)


def get_index_name(file_name: str) -> str:
    """Get index name from file name"""
    file_upper = file_name.upper()
    if 'NIFTY' in file_upper and 'BANK' not in file_upper:
        return 'NIFTY'
    elif 'BANKNIFTY' in file_upper:
        return 'BANKNIFTY'
    elif 'SENSEX' in file_upper:
        return 'SENSEX'
    elif 'FINNIFTY' in file_upper:
        return 'FINNIFTY'
    else:
        return 'UNKNOWN'