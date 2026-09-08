import pandas as pd
import numpy as np
from dataclasses import dataclass
from loguru import logger


@dataclass
class LiquidityAnalysisResult:
    liquidity_score: float = 0
    bid_ask_spread_avg: float = 0
    volume_quality: str = "LOW"
    bias: str = "NEUTRAL"


class LiquidityAnalyzer:
    """Liquidity Analysis"""
    
    def __init__(self, df: pd.DataFrame, atm_strike: float):
        self.df = df
        self.atm_strike = atm_strike
        self.result = LiquidityAnalysisResult()
    
    def analyze(self) -> LiquidityAnalysisResult:
        """Perform liquidity analysis"""
        
        # Get bid-ask spreads
        bid_x = pd.to_numeric(self.df['BID_x'], errors='coerce').fillna(0)
        ask_x = pd.to_numeric(self.df['ASK_x'], errors='coerce').fillna(0)
        bid_y = pd.to_numeric(self.df['BID_y'], errors='coerce').fillna(0)
        ask_y = pd.to_numeric(self.df['ASK_y'], errors='coerce').fillna(0)
        
        # Calculate spreads
        spread_x = ask_x - bid_x
        spread_y = ask_y - bid_y
        
        # Filter valid spreads
        valid_spread_x = spread_x[spread_x > 0]
        valid_spread_y = spread_y[spread_y > 0]
        
        if len(valid_spread_x) > 0 and len(valid_spread_y) > 0:
            avg_spread = (valid_spread_x.mean() + valid_spread_y.mean()) / 2
            self.result.bid_ask_spread_avg = avg_spread
        
        # Calculate volume score
        ce_vol = pd.to_numeric(self.df['VOLUME_x'], errors='coerce').fillna(0).sum()
        pe_vol = pd.to_numeric(self.df['VOLUME_y'], errors='coerce').fillna(0).sum()
        total_volume = ce_vol + pe_vol
        
        # Calculate OI score
        ce_oi = pd.to_numeric(self.df['OI_x'], errors='coerce').fillna(0).sum()
        pe_oi = pd.to_numeric(self.df['OI_y'], errors='coerce').fillna(0).sum()
        total_oi = ce_oi + pe_oi
        
        # Calculate liquidity score (0-100)
        volume_score = min(50, (total_volume / 1000000) * 10)
        oi_score = min(50, (total_oi / 100000) * 10)
        spread_score = max(0, 50 - (self.result.bid_ask_spread_avg * 10))
        
        self.result.liquidity_score = min(100, volume_score + oi_score + spread_score)
        
        # Determine volume quality
        if total_volume > 10000000:
            self.result.volume_quality = "EXTREMELY HIGH"
        elif total_volume > 5000000:
            self.result.volume_quality = "HIGH"
        elif total_volume > 1000000:
            self.result.volume_quality = "MODERATE"
        else:
            self.result.volume_quality = "LOW"
        
        # Determine bias
        if self.result.liquidity_score > 70:
            self.result.bias = "BULLISH"
        elif self.result.liquidity_score > 50:
            self.result.bias = "NEUTRAL"
        else:
            self.result.bias = "BEARISH"
        
        return self.result