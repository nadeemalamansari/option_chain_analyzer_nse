import pandas as pd
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class SupportResistanceResult:
    supports: List[float] = field(default_factory=list)
    resistances: List[float] = field(default_factory=list)
    support_strength: List[str] = field(default_factory=list)
    resistance_strength: List[str] = field(default_factory=list)
    bias: str = "NEUTRAL"


class SupportResistanceAnalyzer:
    """Support and Resistance Analysis"""
    
    def __init__(self, df: pd.DataFrame, atm_strike: float):
        self.df = df
        self.atm_strike = atm_strike
        self.result = SupportResistanceResult()
    
    def analyze(self) -> SupportResistanceResult:
        """Perform Support & Resistance analysis"""
        
        strikes = pd.to_numeric(self.df['STRIKE PRICE'], errors='coerce')
        ce_oi = pd.to_numeric(self.df['OI_x'], errors='coerce').fillna(0)
        pe_oi = pd.to_numeric(self.df['OI_y'], errors='coerce').fillna(0)
        ce_chng = pd.to_numeric(self.df['CHNG_IN_OI_x'], errors='coerce').fillna(0)
        pe_chng = pd.to_numeric(self.df['CHNG_IN_OI_y'], errors='coerce').fillna(0)
        
        # Find support levels (high PE OI below ATM)
        below_atm = strikes < self.atm_strike
        pe_below = pe_oi[below_atm]
        strikes_below = strikes[below_atm]
        
        # Top PE OI strikes below ATM
        top_pe_below = pe_below.nlargest(5)
        self.result.supports = [
            float(strikes_below.iloc[i])
            for i in top_pe_below.index
            if i < len(strikes_below)
        ]
        
        # Find resistance levels (high CE OI above ATM)
        above_atm = strikes > self.atm_strike
        ce_above = ce_oi[above_atm]
        strikes_above = strikes[above_atm]
        
        # Top CE OI strikes above ATM
        top_ce_above = ce_above.nlargest(5)
        self.result.resistances = [
            float(strikes_above.iloc[i])
            for i in top_ce_above.index
            if i < len(strikes_above)
        ]
        
        # Determine strength
        for strike in self.result.supports:
            mask = strikes == strike
            oi_value = pe_oi[mask].values[0] if mask.any() else 0
            chng_value = pe_chng[mask].values[0] if mask.any() else 0
            
            if oi_value > 50000 and chng_value > 0:
                self.result.support_strength.append("VERY STRONG")
            elif oi_value > 25000 and chng_value > 0:
                self.result.support_strength.append("STRONG")
            elif oi_value > 10000:
                self.result.support_strength.append("MODERATE")
            else:
                self.result.support_strength.append("WEAK")
        
        for strike in self.result.resistances:
            mask = strikes == strike
            oi_value = ce_oi[mask].values[0] if mask.any() else 0
            chng_value = ce_chng[mask].values[0] if mask.any() else 0
            
            if oi_value > 50000 and chng_value > 0:
                self.result.resistance_strength.append("VERY STRONG")
            elif oi_value > 25000 and chng_value > 0:
                self.result.resistance_strength.append("STRONG")
            elif oi_value > 10000:
                self.result.resistance_strength.append("MODERATE")
            else:
                self.result.resistance_strength.append("WEAK")
        
        # Determine bias
        if self.result.supports and self.result.resistances:
            if self.result.supports[0] > self.atm_strike - 500:
                self.result.bias = "BULLISH"
            elif self.result.resistances[0] < self.atm_strike + 500:
                self.result.bias = "BEARISH"
            else:
                self.result.bias = "NEUTRAL"
        
        return self.result