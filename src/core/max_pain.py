import pandas as pd
import numpy as np
from typing import Optional
from loguru import logger


class MaxPainCalculator:
    """Calculate Max Pain from Option Chain data"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.strike_col = 'STRIKE PRICE'
    
    def calculate(self) -> float:
        """Calculate Max Pain strike"""
        try:
            strikes = pd.to_numeric(self.df[self.strike_col], errors='coerce')
            
            # Get OI columns
            ce_oi = pd.to_numeric(self.df['OI_x'], errors='coerce').fillna(0)
            pe_oi = pd.to_numeric(self.df['OI_y'], errors='coerce').fillna(0)
            
            # Calculate pain at each strike
            min_pain = float('inf')
            max_pain_strike = strikes.iloc[0]
            
            for i, strike in enumerate(strikes):
                pain = self._calculate_pain_at_strike(strike, strikes, ce_oi, pe_oi)
                if pain < min_pain:
                    min_pain = pain
                    max_pain_strike = strike
            
            return float(max_pain_strike)
            
        except Exception as e:
            logger.error(f"Error calculating Max Pain: {e}")
            return 0.0
    
    def _calculate_pain_at_strike(self, target_strike: float, strikes: pd.Series, 
                                   ce_oi: pd.Series, pe_oi: pd.Series) -> float:
        """Calculate pain at a specific strike"""
        pain = 0.0
        
        for i, strike in enumerate(strikes):
            # CE Pain
            if ce_oi.iloc[i] > 0:
                ce_pain = max(0, target_strike - strike) * ce_oi.iloc[i]
                pain += ce_pain
            
            # PE Pain
            if pe_oi.iloc[i] > 0:
                pe_pain = max(0, strike - target_strike) * pe_oi.iloc[i]
                pain += pe_pain
        
        return pain