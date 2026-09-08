import pandas as pd
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class VolumeAnalysisResult:
    total_ce_volume: float = 0
    total_pe_volume: float = 0
    volume_pcr: float = 0
    ce_concentration: List[Tuple[float, float]] = field(default_factory=list)
    pe_concentration: List[Tuple[float, float]] = field(default_factory=list)
    bias: str = "NEUTRAL"
    volume_quality: str = "LOW"


class VolumeAnalyzer:
    """Volume Analysis"""
    
    def __init__(self, df: pd.DataFrame, atm_strike: float):
        self.df = df
        self.atm_strike = atm_strike
        self.result = VolumeAnalysisResult()
    
    def analyze(self) -> VolumeAnalysisResult:
        """Perform volume analysis"""
        
        # Calculate totals
        ce_vol = pd.to_numeric(self.df['VOLUME_x'], errors='coerce').fillna(0)
        pe_vol = pd.to_numeric(self.df['VOLUME_y'], errors='coerce').fillna(0)
        strikes = pd.to_numeric(self.df['STRIKE PRICE'], errors='coerce')
        
        self.result.total_ce_volume = ce_vol.sum()
        self.result.total_pe_volume = pe_vol.sum()
        
        # Calculate PCR
        if self.result.total_ce_volume > 0:
            self.result.volume_pcr = self.result.total_pe_volume / self.result.total_ce_volume
        
        # Find concentration zones (top 5 strikes by volume)
        top_ce = self.df.nlargest(5, 'VOLUME_x')
        self.result.ce_concentration = [
            (float(pd.to_numeric(row['STRIKE PRICE'], errors='coerce')), 
             float(pd.to_numeric(row['VOLUME_x'], errors='coerce')))
            for _, row in top_ce.iterrows()
        ]
        
        top_pe = self.df.nlargest(5, 'VOLUME_y')
        self.result.pe_concentration = [
            (float(pd.to_numeric(row['STRIKE PRICE'], errors='coerce')), 
             float(pd.to_numeric(row['VOLUME_y'], errors='coerce')))
            for _, row in top_pe.iterrows()
        ]
        
        # Determine volume quality
        total_volume = self.result.total_ce_volume + self.result.total_pe_volume
        if total_volume > 10000000:
            self.result.volume_quality = "EXTREMELY HIGH"
        elif total_volume > 5000000:
            self.result.volume_quality = "HIGH"
        elif total_volume > 1000000:
            self.result.volume_quality = "MODERATE"
        else:
            self.result.volume_quality = "LOW"
        
        # Determine bias
        if self.result.volume_pcr < 0.7:
            self.result.bias = "BULLISH"
        elif self.result.volume_pcr < 0.9:
            self.result.bias = "WEAK BULLISH"
        elif self.result.volume_pcr < 1.1:
            self.result.bias = "NEUTRAL"
        elif self.result.volume_pcr < 1.3:
            self.result.bias = "WEAK BEARISH"
        else:
            self.result.bias = "BEARISH"
        
        return self.result