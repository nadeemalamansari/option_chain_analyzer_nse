import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class ChangeOIAnalysisResult:
    total_ce_chng: float = 0
    total_pe_chng: float = 0
    chng_pcr: float = 0
    ce_writing: List[Tuple[float, float]] = field(default_factory=list)
    pe_writing: List[Tuple[float, float]] = field(default_factory=list)
    ce_unwinding: List[Tuple[float, float]] = field(default_factory=list)
    pe_unwinding: List[Tuple[float, float]] = field(default_factory=list)
    ce_buildup: List[Tuple[float, float]] = field(default_factory=list)
    pe_buildup: List[Tuple[float, float]] = field(default_factory=list)
    bias: str = "NEUTRAL"
    interpretation: str = ""


class ChangeOIAnalyzer:
    """Change in Open Interest Analysis"""
    
    def __init__(self, df: pd.DataFrame, atm_strike: float):
        self.df = df
        self.atm_strike = atm_strike
        self.result = ChangeOIAnalysisResult()
    
    def analyze(self) -> ChangeOIAnalysisResult:
        """Perform Change OI analysis"""
        
        # Calculate totals
        ce_chng = pd.to_numeric(self.df['CHNG_IN_OI_x'], errors='coerce').fillna(0)
        pe_chng = pd.to_numeric(self.df['CHNG_IN_OI_y'], errors='coerce').fillna(0)
        strikes = pd.to_numeric(self.df['STRIKE PRICE'], errors='coerce')
        ce_oi = pd.to_numeric(self.df['OI_x'], errors='coerce').fillna(0)
        pe_oi = pd.to_numeric(self.df['OI_y'], errors='coerce').fillna(0)
        ce_ltp = pd.to_numeric(self.df['LTP_x'], errors='coerce').fillna(0)
        pe_ltp = pd.to_numeric(self.df['LTP_y'], errors='coerce').fillna(0)
        
        self.result.total_ce_chng = ce_chng.sum()
        self.result.total_pe_chng = pe_chng.sum()
        
        # Calculate PCR
        if self.result.total_ce_chng != 0:
            self.result.chng_pcr = self.result.total_pe_chng / self.result.total_ce_chng
        
        # Identify writing (OI increases, price decreases)
        ce_writing_mask = (ce_chng > 0) & (ce_ltp.diff() < 0)
        pe_writing_mask = (pe_chng > 0) & (pe_ltp.diff() < 0)
        
        self.result.ce_writing = [
            (float(strikes.iloc[i]), float(ce_chng.iloc[i]))
            for i in ce_writing_mask[ce_writing_mask].index
            if i < len(strikes)
        ][:5]
        
        self.result.pe_writing = [
            (float(strikes.iloc[i]), float(pe_chng.iloc[i]))
            for i in pe_writing_mask[pe_writing_mask].index
            if i < len(strikes)
        ][:5]
        
        # Identify unwinding (OI decreases)
        ce_unwind_mask = ce_chng < 0
        pe_unwind_mask = pe_chng < 0
        
        self.result.ce_unwinding = [
            (float(strikes.iloc[i]), float(abs(ce_chng.iloc[i])))
            for i in ce_unwind_mask[ce_unwind_mask].index
            if i < len(strikes)
        ][:5]
        
        self.result.pe_unwinding = [
            (float(strikes.iloc[i]), float(abs(pe_chng.iloc[i])))
            for i in pe_unwind_mask[pe_unwind_mask].index
            if i < len(strikes)
        ][:5]
        
        # Identify buildup (OI increases, price increases)
        ce_buildup_mask = (ce_chng > 0) & (ce_ltp.diff() > 0)
        pe_buildup_mask = (pe_chng > 0) & (pe_ltp.diff() > 0)
        
        self.result.ce_buildup = [
            (float(strikes.iloc[i]), float(ce_chng.iloc[i]))
            for i in ce_buildup_mask[ce_buildup_mask].index
            if i < len(strikes)
        ][:5]
        
        self.result.pe_buildup = [
            (float(strikes.iloc[i]), float(pe_chng.iloc[i]))
            for i in pe_buildup_mask[pe_buildup_mask].index
            if i < len(strikes)
        ][:5]
        
        # Determine bias
        self._determine_bias()
        
        return self.result
    
    def _determine_bias(self):
        """Determine bias based on Change OI patterns"""
        ce_net = self.result.total_ce_chng
        pe_net = self.result.total_pe_chng
        
        if pe_net > ce_net * 1.5:
            self.result.bias = "STRONG BEARISH"
            self.result.interpretation = "Heavy put addition indicates strong hedging"
        elif pe_net > ce_net * 1.2:
            self.result.bias = "BEARISH"
            self.result.interpretation = "More put addition than calls"
        elif ce_net > pe_net * 1.5:
            self.result.bias = "STRONG BULLISH"
            self.result.interpretation = "Heavy call addition indicates strong buying"
        elif ce_net > pe_net * 1.2:
            self.result.bias = "BULLISH"
            self.result.interpretation = "More call addition than puts"
        else:
            self.result.bias = "NEUTRAL"
            self.result.interpretation = "Balanced addition in calls and puts"