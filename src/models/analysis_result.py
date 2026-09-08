"""
Analysis result models
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum


class Verdict(Enum):
    """Market verdict enum"""
    STRONG_BULLISH = "STRONG BULLISH"
    BULLISH = "BULLISH"
    WEAK_BULLISH = "WEAK BULLISH"
    NEUTRAL = "NEUTRAL"
    WEAK_BEARISH = "WEAK BEARISH"
    BEARISH = "BEARISH"
    STRONG_BEARISH = "STRONG BEARISH"


class Bias(Enum):
    """Bias enum"""
    STRONG_BULLISH = "STRONG BULLISH"
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"
    STRONG_BEARISH = "STRONG BEARISH"


@dataclass
class FactorScore:
    """Individual factor score"""
    name: str
    score: float
    weight: float
    bias: Bias
    contribution: float = 0
    
    @property
    def weighted_score(self) -> float:
        return self.score * self.weight / 100


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    # File Info
    file_name: str = ""
    exchange: str = "NSE"
    expiry: str = ""
    
    # ATM Data
    atm_strike: float = 0
    atm_ce_oi: float = 0
    atm_pe_oi: float = 0
    atm_ce_ltp: float = 0
    atm_pe_ltp: float = 0
    atm_ce_iv: float = 0
    atm_pe_iv: float = 0
    atm_ce_volume: float = 0
    atm_pe_volume: float = 0
    
    # OI Analysis
    total_ce_oi: float = 0
    total_pe_oi: float = 0
    oi_pcr: float = 0
    highest_ce_oi_strike: float = 0
    highest_pe_oi_strike: float = 0
    ce_oi_concentration: List[Tuple[float, float]] = field(default_factory=list)
    pe_oi_concentration: List[Tuple[float, float]] = field(default_factory=list)
    oi_positioning_bias: Bias = Bias.NEUTRAL
    
    # Change OI Analysis
    total_ce_chng: float = 0
    total_pe_chng: float = 0
    chng_oi_pcr: float = 0
    ce_writing: List[Tuple[float, float]] = field(default_factory=list)
    pe_writing: List[Tuple[float, float]] = field(default_factory=list)
    ce_unwinding: List[Tuple[float, float]] = field(default_factory=list)
    pe_unwinding: List[Tuple[float, float]] = field(default_factory=list)
    change_oi_bias: Bias = Bias.NEUTRAL
    
    # Volume Analysis
    total_ce_volume: float = 0
    total_pe_volume: float = 0
    volume_pcr: float = 0
    ce_volume_concentration: List[Tuple[float, float]] = field(default_factory=list)
    pe_volume_concentration: List[Tuple[float, float]] = field(default_factory=list)
    volume_bias: Bias = Bias.NEUTRAL
    
    # Support & Resistance
    supports: List[float] = field(default_factory=list)
    resistances: List[float] = field(default_factory=list)
    support_strength: List[str] = field(default_factory=list)
    resistance_strength: List[str] = field(default_factory=list)
    sr_bias: Bias = Bias.NEUTRAL
    
    # Max Pain
    max_pain: float = 0
    
    # Liquidity
    liquidity_score: float = 0
    liquidity_bias: Bias = Bias.NEUTRAL
    
    # OI Migration
    oi_migration: str = "NO CLEAR SHIFT"
    
    # Factor Scores
    factor_scores: List[FactorScore] = field(default_factory=list)
    bullish_score: float = 0
    bearish_score: float = 0
    
    # Final
    final_verdict: Verdict = Verdict.NEUTRAL
    confidence: float = 0
    factor_agreement: str = "NEUTRAL"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'file_name': self.file_name,
            'exchange': self.exchange,
            'expiry': self.expiry,
            'atm_strike': self.atm_strike,
            'oi_pcr': self.oi_pcr,
            'chng_oi_pcr': self.chng_oi_pcr,
            'volume_pcr': self.volume_pcr,
            'max_pain': self.max_pain,
            'bullish_score': self.bullish_score,
            'bearish_score': self.bearish_score,
            'final_verdict': self.final_verdict.value,
            'confidence': self.confidence,
            'factor_agreement': self.factor_agreement,
            'oi_migration': self.oi_migration,
            'supports': self.supports,
            'resistances': self.resistances
        }