"""
Constants for Option Chain Analyzer
"""

# Indices
INDICES = {
    "NIFTY": {"symbol": "NIFTY", "lot_size": 50, "exchange": "NSE"},
    "BANKNIFTY": {"symbol": "BANKNIFTY", "lot_size": 25, "exchange": "NSE"},
    "SENSEX": {"symbol": "SENSEX", "lot_size": 15, "exchange": "BSE"},
    "FINNIFTY": {"symbol": "FINNIFTY", "lot_size": 40, "exchange": "NSE"}
}

# PCR Thresholds
PCR_THRESHOLDS = {
    "STRONG_BULLISH": 0.70,
    "BULLISH": 0.90,
    "NEUTRAL_LOW": 0.91,
    "NEUTRAL_HIGH": 1.10,
    "BEARISH": 1.30,
    "STRONG_BEARISH": 1.50
}

# Verdict Colors
VERDICT_COLORS = {
    "STRONG BULLISH": "#00cc66",
    "BULLISH": "#88dd88",
    "WEAK BULLISH": "#ccdd88",
    "NEUTRAL": "#ffaa00",
    "WEAK BEARISH": "#dd8866",
    "BEARISH": "#dd4444",
    "STRONG BEARISH": "#cc0000"
}

# OI Thresholds
OI_THRESHOLDS = {
    "VERY_HIGH": 100000,
    "HIGH": 50000,
    "MODERATE": 25000,
    "LOW": 10000
}

# Volume Thresholds
VOLUME_THRESHOLDS = {
    "EXTREMELY_HIGH": 10000000,
    "HIGH": 5000000,
    "MODERATE": 1000000,
    "LOW": 100000
}

# Support & Resistance Configuration
SUPPORT_RESISTANCE_CONFIG = {
    "lookback_strikes": 5,
    "min_oi_for_support": 10000,
    "min_oi_for_resistance": 10000,
    "concentration_pct": 0.70
}

# Factor Weights
FACTOR_WEIGHTS = {
    "oi_positioning": 0.25,
    "change_oi": 0.20,
    "volume": 0.15,
    "support_resistance": 0.20,
    "pcr": 0.10,
    "liquidity": 0.10
}

# Chart Colors
CHART_COLORS = {
    "ce": "#00cc66",
    "pe": "#ff4444",
    "atm": "#ffaa00",
    "support": "#00aaff",
    "resistance": "#ff6600",
    "background": "#0e1117",
    "grid": "#262730"
}

# Default Expiry Dates (for display)
DEFAULT_EXPIRIES = {
    "weekly": "Thursday",
    "monthly": "Last Thursday",
    "quarterly": "Quarter End"
}