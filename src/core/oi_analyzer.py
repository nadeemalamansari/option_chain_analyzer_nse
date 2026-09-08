import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class OIAnalysisResult:
    total_ce_oi: float = 0
    total_pe_oi: float = 0
    oi_pcr: float = 0
    highest_ce_strike: float = 0
    highest_pe_strike: float = 0
    ce_concentration: List[Tuple[float, float]] = field(default_factory=list)
    pe_concentration: List[Tuple[float, float]] = field(default_factory=list)
    bias: str = "NEUTRAL"


class OIAnalyzer:
    """Open Interest Analysis"""
    
    def __init__(self, df: pd.DataFrame, atm_strike: float):
        self.df = df
        self.atm_strike = atm_strike
        self.result = OIAnalysisResult()
    
    def analyze(self) -> OIAnalysisResult:
        """Perform OI analysis"""
        
        # Calculate totals
        ce_oi = pd.to_numeric(self.df['OI_x'], errors='coerce').fillna(0)
        pe_oi = pd.to_numeric(self.df['OI_y'], errors='coerce').fillna(0)
        strikes = pd.to_numeric(self.df['STRIKE PRICE'], errors='coerce')
        
        self.result.total_ce_oi = ce_oi.sum()
        self.result.total_pe_oi = pe_oi.sum()
        
        # Calculate PCR
        if self.result.total_ce_oi > 0:
            self.result.oi_pcr = self.result.total_pe_oi / self.result.total_ce_oi
        
        # Find highest OI strikes
        self.result.highest_ce_strike = strikes.iloc[ce_oi.idxmax()]
        self.result.highest_pe_strike = strikes.iloc[pe_oi.idxmax()]
        
        # Find concentration zones (top 5 strikes)
        top_ce = self.df.nlargest(5, 'OI_x')
        self.result.ce_concentration = [
            (float(pd.to_numeric(row['STRIKE PRICE'], errors='coerce')), 
             float(pd.to_numeric(row['OI_x'], errors='coerce')))
            for _, row in top_ce.iterrows()
        ]
        
        top_pe = self.df.nlargest(5, 'OI_y')
        self.result.pe_concentration = [
            (float(pd.to_numeric(row['STRIKE PRICE'], errors='coerce')), 
             float(pd.to_numeric(row['OI_y'], errors='coerce')))
            for _, row in top_pe.iterrows()
        ]
        
        # Determine bias
        if self.result.oi_pcr < 0.8:
            self.result.bias = "BULLISH"
        elif self.result.oi_pcr < 1.2:
            self.result.bias = "NEUTRAL"
        else:
            self.result.bias = "BEARISH"
        
        return self.result