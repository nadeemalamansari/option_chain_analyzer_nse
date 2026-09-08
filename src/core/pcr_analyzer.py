import pandas as pd
import numpy as np
from dataclasses import dataclass
from loguru import logger


@dataclass
class PCRAnalysisResult:
    oi_pcr: float = 0
    chng_pcr: float = 0
    volume_pcr: float = 0
    bias: str = "NEUTRAL"
    interpretation: str = ""


class PCRAnalyzer:
    """Put-Call Ratio Analysis"""
    
    def __init__(self, df: pd.DataFrame, atm_strike: float):
        self.df = df
        self.atm_strike = atm_strike
        self.result = PCRAnalysisResult()
    
    def analyze(self) -> PCRAnalysisResult:
        """Perform PCR analysis"""
        
        # Calculate OI PCR
        ce_oi = pd.to_numeric(self.df['OI_x'], errors='coerce').fillna(0).sum()
        pe_oi = pd.to_numeric(self.df['OI_y'], errors='coerce').fillna(0).sum()
        
        if ce_oi > 0:
            self.result.oi_pcr = pe_oi / ce_oi
        
        # Calculate Change OI PCR
        ce_chng = pd.to_numeric(self.df['CHNG_IN_OI_x'], errors='coerce').fillna(0).sum()
        pe_chng = pd.to_numeric(self.df['CHNG_IN_OI_y'], errors='coerce').fillna(0).sum()
        
        if ce_chng != 0:
            self.result.chng_pcr = pe_chng / ce_chng
        
        # Calculate Volume PCR
        ce_vol = pd.to_numeric(self.df['VOLUME_x'], errors='coerce').fillna(0).sum()
        pe_vol = pd.to_numeric(self.df['VOLUME_y'], errors='coerce').fillna(0).sum()
        
        if ce_vol > 0:
            self.result.volume_pcr = pe_vol / ce_vol
        
        # Determine bias and interpretation
        self._determine_bias()
        
        return self.result
    
    def _determine_bias(self):
        """Determine bias based on PCR values"""
        if self.result.oi_pcr < 0.7 and self.result.chng_pcr < 0.8:
            self.result.bias = "STRONG BULLISH"
            self.result.interpretation = "Very low PCR indicates strong bullish sentiment"
        elif self.result.oi_pcr < 0.9:
            self.result.bias = "BULLISH"
            self.result.interpretation = "Low PCR indicates bullish sentiment"
        elif self.result.oi_pcr < 1.1:
            self.result.bias = "NEUTRAL"
            self.result.interpretation = "PCR near 1 indicates balanced sentiment"
        elif self.result.oi_pcr < 1.3:
            self.result.bias = "BEARISH"
            self.result.interpretation = "High PCR indicates bearish sentiment / hedging"
        else:
            self.result.bias = "STRONG BEARISH"
            self.result.interpretation = "Very high PCR indicates strong bearish sentiment / hedging"